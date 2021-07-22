import hashlib
import json
import logging
import mimetypes
import re
import subprocess
from collections import Generator
from datetime import datetime
from fnmatch import fnmatch
from pathlib import Path
from typing import Iterable, List, Optional

import pytz
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

from backend import settings
from backup.models.source import BaseSource
from backup.utils.datetime import parse_exif_date, datetime_to_json, json_to_datetime
from backup.utils.geo import dms_to_decimal
from timeline.models import Entry

logger = logging.getLogger(__name__)


class FileFormatError(Exception):
    """
    This exception is raised when a file can't be read properly. For example, an unreadable image or an invalid JSON
    file.
    """
    pass


def get_file_entry_date(entry: Entry) -> datetime:
    """
    Returns the most appropriate timeline date for a file, picking the earliest date of many candidates
    """
    file_path = Path(entry.extra_attributes['file']['path'])
    filename_date = get_filename_date(file_path)
    modification_date = get_file_modification_date(file_path)
    try:
        exif_date = json_to_datetime(entry.extra_attributes['media']['creation_date'])
    except KeyError:
        exif_date = None

    return min(filter(None, (filename_date, modification_date, exif_date)))


def get_file_modification_date(file_path: Path) -> datetime:
    return datetime.fromtimestamp(file_path.stat().st_mtime, pytz.UTC)


def get_filename_date(file_path: Path) -> Optional[datetime]:
    default_timezone = 'Europe/Berlin'  # TODO: If this thing gets a million users, that assumption could be wrong
    date_regex = "(\\d{4})-([0][1-9]|1[0-2])-([0-2][1-9]|[1-3]0|3[01])"
    if matches := re.search(f'.*({date_regex})$', file_path.stem):
        try:
            return pytz.timezone(default_timezone) \
                .localize(datetime.strptime(matches.groups()[0], '%Y-%m-%d')) \
                .replace(hour=12) \
                .astimezone(pytz.UTC)
        except ValueError:
            pass
    else:
        return None


def get_files_in_dir(dir_path: Path) -> Generator[Path, None, None]:
    for path in dir_path.rglob('*'):
        if path.is_file():
            yield path


def get_include_rules_for_dir(dir_path: Path, includefile_name: str) -> Generator[Path, None, None]:
    timelineinclude_paths = dir_path.rglob(includefile_name)
    for timelineinclude_path in timelineinclude_paths:
        with open(timelineinclude_path, 'r') as timelineinclude_file:
            for line in timelineinclude_file.readlines():
                glob_path = timelineinclude_path.parent / Path(line.strip())
                relative_glob_path = glob_path.relative_to(dir_path)
                yield dir_path / relative_glob_path


def get_files_matching_rules(files: Iterable[Path], rules: Iterable[Path]) -> Generator[Path, None, None]:
    for file in files:
        # Path.match() doesn't match ** to multiple subdirs, so we use fnmatch
        if any(fnmatch(str(file), str(rule)) for rule in rules):
            yield file


def get_mimetype(file_path: Path) -> str:
    return mimetypes.guess_type(file_path, strict=False)[0]


def get_schema_from_mimetype(mimetype) -> str:
    schema = 'file'
    if not mimetype:
        return schema

    if mimetype.startswith('image/'):
        schema += '.image'
    elif mimetype.startswith('video/'):
        # TODO: Some MP4 files are audio only, but recognised as videos
        schema += '.video'
    elif mimetype.startswith('audio/'):
        schema += '.audio'
    elif mimetype.startswith('text/'):
        # TODO: Handle text/markdown
        schema += '.text'
    elif mimetype == 'application/pdf':
        schema += '.document.pdf'

    return schema


def create_entries_from_directory(path: Path, source: BaseSource, backup_date: datetime, use_cache=True) -> List[Entry]:
    """
    Delete and recreate the Entries for the files in a directory.
    """
    timelineinclude_rules = list(get_include_rules_for_dir(path, settings.TIMELINE_INCLUDE_FILE))
    files = list(get_files_matching_rules(get_files_in_dir(path), timelineinclude_rules))

    inode_checksum_cache = {}  # translates file inodes to checksums
    metadata_cache = {}  # translates checksums to entry metadata
    cached_extra_attributes = ('location', 'media', 'previews')
    if use_cache:
        # Most files in a directory already have a matching Entry. Recalculating the metadata for each file Entry is
        # wasteful and time-consuming.
        # Instead, we build a cache of all files that have an Entry. If we process a file that already has an Entry (if
        # they have the same inode), we can reuse the cached Entry metadata.
        for entry in source.get_entries():
            try:
                # We also avoid calculating checksums if we don't have to. Instead, we compare the file inodes. If the
                # inodes are the same, THEN we calculate and compare the checksums. If the file in the Entry and the
                # file in the directory have the same checksum, then they're identical, and we can reuse the metadata.
                entry_file_inode = Path(entry.extra_attributes['file']['path']).stat().st_ino
                inode_checksum_cache[entry_file_inode] = entry.extra_attributes['file']['checksum']
            except FileNotFoundError:
                # This can happen if the file in the Entry was deleted or moved.
                pass

            metadata = {}

            for attribute in cached_extra_attributes:
                if attribute in entry.extra_attributes:
                    metadata[attribute] = entry.extra_attributes[attribute]

            if entry.description:
                metadata['description'] = entry.description

            metadata_cache[entry.extra_attributes['file']['checksum']] = metadata

    entries_to_create = []
    for file in files:
        file.resolve()

        try:
            checksum = inode_checksum_cache.get(file.stat().st_ino) or get_checksum(file)
        except OSError:
            logger.exception(f"Could not generate checksum for {str(file)}")
            raise

        if checksum in metadata_cache:
            mimetype = get_mimetype(file)
            entry = Entry(
                title=file.name,
                source=source.entry_source,
                schema=get_schema_from_mimetype(mimetype),
                description=metadata_cache[checksum].get('description', ''),
                extra_attributes={
                    'file': {
                        'path': str(file),
                        'checksum': checksum,
                        'mimetype': mimetype,
                    },
                }
            )

            for attribute in cached_extra_attributes:
                if attribute in metadata_cache:
                    entry.extra_attributes[attribute] = metadata_cache[attribute]
        else:
            entry = entry_from_file_path(file, source)

        entry.extra_attributes['backup_date'] = datetime_to_json(backup_date)

        entry.date_on_timeline = get_file_entry_date(entry)  # This could change, so it's not cached
        entries_to_create.append(entry)

    source.get_entries().delete()  # TODO: Only delete the entries in the specified directory?
    return Entry.objects.bulk_create(entries_to_create)


def entry_from_file_path(file_path: Path, source: BaseSource) -> Entry:
    """
    Creates an Entry template from a file path, filling the fields with file metadata.
    """
    mimetype = get_mimetype(file_path)
    entry = Entry(
        title=file_path.name,
        source=source.entry_source,
        schema=get_schema_from_mimetype(mimetype),
        extra_attributes={
            'file': {
                'checksum': get_checksum(file_path),
                'path': str(file_path.resolve()),
                'mimetype': mimetype,
            },
        },
    )
    entry.date_on_timeline = get_file_entry_date(entry)

    if mimetype:
        if mimetype.startswith('image/'):
            entry.schema = 'file.image'
            entry.extra_attributes.update(get_image_extra_attributes(file_path))
        if mimetype.startswith('video/'):
            entry.schema = 'file.video'
            try:
                entry.extra_attributes.update(get_video_extra_attributes(file_path))
            except FileFormatError:
                logger.exception(f"Could not read metadata for video {str(file_path)}")
        if mimetype.startswith('audio/'):
            entry.schema = 'file.audio'
            entry.extra_attributes.update(get_audio_extra_attributes(file_path))
        if mimetype.startswith('text/'):
            entry.schema = 'file.text'
            with file_path.open('r') as text_file:
                entry.description = text_file.read(settings.MAX_PLAINTEXT_PREVIEW_SIZE)

    return entry


def get_image_extra_attributes(file_path: Path) -> dict:
    with Image.open(file_path) as image:
        width, height = image.size
        assert width > 0 and height > 0, "Invalid image dimensions"

    metadata = {
        'media': {
            'width': width,
            'height': height,
        },
    }

    exif = get_image_exif(file_path)

    # Camera info
    if 'Make' in exif or 'Model' in exif:
        metadata['media']['camera'] = f"{exif.get('Make', '')} {exif.get('Model', '')}".replace('\x00', '').strip()

    # Geolocation
    if 'GPSInfo' in exif:
        metadata['location'] = {}
        if 'GPSLatitude' in exif['GPSInfo'] and 'GPSLongitude' in exif['GPSInfo']:
            metadata['location']['latitude'] = dms_to_decimal(
                exif['GPSInfo']['GPSLatitude'], exif['GPSInfo'].get('GPSLatitudeRef')
            )
            metadata['location']['longitude'] = dms_to_decimal(
                exif['GPSInfo']['GPSLongitude'], exif['GPSInfo'].get('GPSLongitudeRef')
            )
        if 'GPSAltitude' in exif['GPSInfo']:
            altitude = exif['GPSInfo']['GPSAltitude']
            if not exif['GPSInfo'].get('GPSAltitudeRef', b'\x00') == b'\x00':
                altitude *= -1
            try:
                metadata['location']['altitude'] = float(altitude)
            except ZeroDivisionError:
                logger.warning(f"Division by zero for altitude {altitude} - {file_path}")
        if 'GPSImgDirection' in exif['GPSInfo']:
            try:
                metadata['location']['direction'] = float(exif['GPSInfo']['GPSImgDirection'])
            except ZeroDivisionError:
                logger.warning(f"Division by zero for direction {exif['GPSInfo']['GPSImgDirection']} - {file_path}")
        if 'GPSDestBearing' in exif['GPSInfo']:
            try:
                metadata['location']['bearing'] = float(exif['GPSInfo']['GPSDestBearing'])
            except ZeroDivisionError:
                logger.warning(f"Division by zero for bearing {exif['GPSInfo']['GPSDestBearing']} - {file_path}")

    # Camera orientation
    if 'Orientation' in exif:
        orientation_map = {0: 0, 1: 0, 3: 180, 6: 270, 8: 90}  # 0 is not an official value, but it happens
        try:
            metadata['media']['orientation'] = orientation_map[exif['Orientation']]
        except KeyError:
            logger.warning(f"{file_path} had unexpected EXIF orientation: {exif['Orientation']}")

        # Set the correct width/height according to EXIF orientation
        if metadata['media']['orientation'] == 90 or metadata['media']['orientation'] == 270:
            width = metadata['media']['width']
            height = metadata['media']['height']
            metadata['media']['width'] = height
            metadata['media']['height'] = width
            del metadata['media']['orientation']

    # Date
    if 'GPSDateStamp' in exif.get('GPSInfo', {}) and 'GPSTimeStamp' in exif.get('GPSInfo', {}):
        gps_datetime = ''  # GPS dates are UTC
        try:
            gps_date = exif['GPSInfo']['GPSDateStamp']
            gps_time = ":".join(f"{int(timefragment):02}" for timefragment in exif['GPSInfo']['GPSTimeStamp'])
            gps_datetime = f"{gps_date} {gps_time}"
            metadata['media'] = metadata.get('media', {})
            metadata['media']['creation_date'] = datetime_to_json(parse_exif_date(gps_datetime))
        except ValueError:
            logging.exception(f"Could not parse EXIF GPS date '{gps_datetime} ({file_path})'")
        except KeyError:
            pass
    elif exif_date := (exif.get('DateTimeOriginal') or exif.get('DateTime')):
        # There is no timezone information on exif dates
        try:
            metadata['media'] = metadata.get('media', {})
            metadata['media']['creation_date'] = datetime_to_json(parse_exif_date(exif_date))
        except ValueError:
            logging.exception(f"Could not parse EXIF date '{exif_date}' ({file_path})")

    return metadata


def get_audio_extra_attributes(file_path: Path) -> dict:
    ffprobe_cmd = subprocess.run(
        [
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'a',
            '-show_entries', 'stream=duration,codec_name',
            '-of', 'json',
            str(file_path)
        ],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    if audio_streams := json.loads(ffprobe_cmd.stdout.decode('utf-8'))['streams']:
        return {
            'media': {
                'duration': int(float(audio_streams[0]['duration'])),
                'codec': audio_streams[0]['codec_name'],
            }
        }
    else:
        return {}


def get_video_extra_attributes(file_path: Path) -> dict:
    # TODO: Extract video geolocation

    ffprobe_cmd = subprocess.run(
        [
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'v',
            '-show_format', '-show_streams',
            '-of', 'json',
            str(file_path)
        ],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    try:
        video_streams = json.loads(ffprobe_cmd.stdout.decode('utf-8'))['streams']
    except KeyError:
        raise FileFormatError(f"Could not read streams of video file {str(file_path)}.")

    if video_streams:
        metadata = {
            'media': {
                'width': int(video_streams[0]['width']),
                'height': int(video_streams[0]['height'])
            }
        }
        if 'duration' in video_streams[0]:
            metadata['media']['duration'] = int(float(video_streams[0]['duration']))
        if 'codec_name' in video_streams[0]:
            metadata['media']['codec'] = video_streams[0].get('codec_name')
        if 'rotate' in video_streams[0].get('tags', {}):
            metadata['media']['orientation'] = int(video_streams[0]['tags']['rotate'])
        if 'creation_time' in video_streams[0].get('tags', {}):
            creation_time = json_to_datetime(video_streams[0]['tags']['creation_time'])
            metadata['media']['creation_date'] = datetime_to_json(creation_time)

        return metadata
    else:
        return {}


def get_checksum(file_path: Path) -> str:
    with open(file_path, "rb") as f:
        file_hash = hashlib.blake2b()
        while chunk := f.read(8192):
            file_hash.update(chunk)
    return file_hash.hexdigest()


def get_image_exif(input_path: Path) -> dict:
    with Image.open(input_path) as image:  # https://github.com/python-pillow/Pillow/issues/4007
        image.verify()

    with Image.open(input_path) as image:
        raw_exif = image.getexif()

    if not raw_exif:
        return {}

    exif = {}
    for (key, val) in raw_exif.items():
        exif[TAGS.get(key)] = val

    gpsinfo_tags = {}
    if 'GPSInfo' in exif:
        for (key, val) in GPSTAGS.items():
            if key in exif['GPSInfo']:
                gpsinfo_tags[val] = exif['GPSInfo'][key]

        exif['GPSInfo'] = gpsinfo_tags

    return exif
