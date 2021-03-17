import hashlib
import json
import logging
import mimetypes
import subprocess
from collections import Generator
from datetime import datetime
from fnmatch import fnmatch
from pathlib import Path
from typing import Iterable, List

import pytz
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

from backend import settings
from backup.models.base import BaseSource
from timeline.geo_utils import dms_to_decimal
from timeline.models import Entry

logger = logging.getLogger(__name__)


def get_modification_date(file_path: Path) -> datetime:
    return datetime.fromtimestamp(file_path.stat().st_mtime, pytz.UTC)


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
        schema += '.video'
    elif mimetype.startswith('audio/'):
        schema += '.audio'
    elif mimetype.startswith('text/'):
        # TODO: Handle text/markdown
        schema += '.text'
    elif mimetype == 'application/pdf':
        schema += '.document.pdf'

    return schema


def create_entries_from_files(files: Iterable[Path], source: BaseSource, backup_date: datetime) -> List[Entry]:
    entries_to_create = []
    for file in files:
        mimetype = get_mimetype(file)
        schema = get_schema_from_mimetype(mimetype)
        entry = Entry(
            schema=schema,
            source=source.entry_source,
            title=file.name,
            description='',
            date_on_timeline=get_modification_date(file),
            extra_attributes={
                'file': {
                    'path': str(file.resolve()),
                    'checksum': get_checksum(file),
                },
                'backup_date': backup_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
            }
        )

        if mimetype:
            entry.extra_attributes['file']['mimetype'] = mimetype

        if schema == 'file.text' or schema.startswith('file.text'):
            try:
                _set_plaintext_description(entry)
            except:
                logger.exception(
                    f"Could not set plain text description for file {entry.extra_attributes['file']['path']}")

        if schema.startswith('file.image') or schema.startswith('file.video'):
            try:
                _set_media_metadata(entry)
            except:
                logger.exception(f"Could not set media metadata for file {entry.extra_attributes['file']['path']}")

        if schema == 'file.image' or schema.startswith('file.image'):
            try:
                _set_exif_metadata(entry)
            except:
                logger.exception(f"Could not set exif metadata for file {entry.extra_attributes['file']['path']}")

        entries_to_create.append(entry)

    return Entry.objects.bulk_create(entries_to_create)


def _set_media_metadata(entry: Entry):
    """
    Sets width, height, duration and codec attributes for media files
    """
    if 'media' in entry.extra_attributes:
        # Information is already set
        return

    entry.extra_attributes['media'] = {}
    original_path = Path(entry.extra_attributes['file']['path'])
    try:
        original_media_attrs = get_media_metadata(original_path)
        entry.extra_attributes['media'].update(original_media_attrs)
        if (
            entry.extra_attributes['file'].get('mimetype').startswith('image')
            and 'codec' in entry.extra_attributes['media']
        ):
            # JPEG images are treated as MJPEG videos and have a duration of 1 frame
            entry.extra_attributes['media'].pop('duration', None)
            entry.extra_attributes['media'].pop('codec', None)
    except:
        logger.exception(f"Could not read metadata from file {original_path}")
        raise


def _set_exif_metadata(entry: Entry):
    if 'camera' in entry.extra_attributes.get('media', {}) or 'location' in entry.extra_attributes:
        # TODO: Photos with missing exif data will be reprocessed
        return

    original_path = Path(entry.extra_attributes['file']['path'])
    try:
        metadata = get_metadata_from_exif(original_path)
        if 'media' in metadata:
            entry.extra_attributes['media'].update(metadata['media'])
        if 'location' in metadata:
            entry.extra_attributes['location'] = metadata['location']
    except:
        logger.exception(f"Could not read exif from file {original_path}")
        raise


def _set_plaintext_description(entry: Entry):
    """
    Sets the description attribute for plain text files
    """
    if len(entry.description):
        return
    original_path = Path(entry.extra_attributes['file']['path'])
    with original_path.open('r') as text_file:
        entry.description = text_file.read(settings.MAX_PLAINTEXT_PREVIEW_SIZE)


def get_checksum(file_path: Path) -> str:
    with open(file_path, "rb") as f:
        file_hash = hashlib.blake2b()
        while chunk := f.read(8192):
            file_hash.update(chunk)
    return file_hash.hexdigest()


def get_media_metadata(input_path: Path) -> dict:
    ffprobe_cmd = subprocess.run(
        [
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'v',
            '-show_entries', 'stream=width,height,duration,codec_name',
            '-of', 'json',
            str(input_path)
        ],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    raw_metadata = json.loads(ffprobe_cmd.stdout.decode('utf-8'))['streams'][0]

    metadata = {
        'width': int(raw_metadata['width']),
        'height': int(raw_metadata['height']),
    }

    if 'duration' in raw_metadata:
        metadata['duration'] = int(float(raw_metadata['duration']))  # Note: images can also have a duration
    if 'codec_name' in raw_metadata:
        metadata['codec'] = raw_metadata['codec_name']

    return metadata


def get_exif(input_path: Path) -> dict:
    image = Image.open(input_path)
    image.verify()
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


def get_metadata_from_exif(input_path: Path) -> dict:
    metadata = {}
    try:
        exif = get_exif(input_path)
    except:
        return metadata

    if 'GPSInfo' in exif:
        metadata['location'] = {}
        if 'GPSLatitude' in exif['GPSInfo'] and 'GPSLongitude' in exif['GPSInfo']:
            metadata['location'].update({
                'latitude': dms_to_decimal(exif['GPSInfo']['GPSLatitude'], exif['GPSInfo'].get('GPSLatitudeRef')),
                'longitude': dms_to_decimal(exif['GPSInfo']['GPSLongitude'], exif['GPSInfo'].get('GPSLongitudeRef')),
            })

        if 'GPSAltitude' in exif['GPSInfo']:
            altitude = exif['GPSInfo']['GPSAltitude']
            if not exif['GPSInfo'].get('GPSAltitudeRef', b'\x00') == b'\x00':
                altitude *= -1
            metadata['location']['altitude'] = float(altitude)

        if 'GPSImgDirection' in exif['GPSInfo']:
            metadata['location']['direction'] = float(exif['GPSInfo']['GPSImgDirection'])

        if 'GPSDestBearing' in exif['GPSInfo']:
            metadata['location']['bearing'] = float(exif['GPSInfo']['GPSDestBearing'])

    if 'Make' in exif or 'Model' in exif:
        metadata['media'] = metadata.get('media', {})
        metadata['media']['camera'] = f"{exif.get('Make', '')} {exif.get('Model', '')}".replace('\x00', '').strip()

    if 'GPSDateStamp' in exif.get('GPSInfo', {}) and 'GPSTimeStamp' in exif.get('GPSInfo', {}):
        # GPS dates are UTC
        try:
            gps_date = exif['GPSInfo']['GPSDateStamp']
            gps_time = ":".join(f"{float(timefragment):02.0f}" for timefragment in exif['GPSInfo']['GPSTimeStamp'])
            metadata['media'] = metadata.get('media', {})
            metadata['media']['creation_date'] = datetime\
                .strptime(f"{gps_date} {gps_time}".replace('\x00', '').replace('-', ':'), '%Y:%m:%d %H:%M:%S')\
                .strftime('%Y-%m-%dT%H:%M:%SZ')
        except KeyError:
            pass
    elif 'DateTimeOriginal' in exif:
        # There is no timezone information on this date
        metadata['media'] = metadata.get('media', {})
        metadata['media']['creation_date'] = datetime\
            .strptime(exif['DateTimeOriginal'].replace('\x00', '').replace('-', ':'), '%Y:%m:%d %H:%M:%S')\
            .strftime('%Y-%m-%dT%H:%M:%SZ')

    return metadata
