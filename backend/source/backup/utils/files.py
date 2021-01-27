import hashlib
import json
import logging
import mimetypes
import subprocess
from datetime import datetime
from pathlib import Path
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

from timeline.geo_utils import dms_to_decimal

logger = logging.getLogger(__name__)


def get_mimetype(file_path: Path) -> str:
    return mimetypes.guess_type(file_path, strict=False)[0]


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
        metadata['camera'] = f"{exif.get('Make', '')} {exif.get('Model', '')}".replace('\x00', '').strip()

    if 'GPSDateStamp' in exif.get('GPSInfo', {}) and 'GPSTimeStamp' in exif.get('GPSInfo', {}):
        # GPS dates are UTC
        try:
            gps_date = exif['GPSInfo']['GPSDateStamp']
            gps_time = ":".join(f"{float(timefragment):02.0f}" for timefragment in exif['GPSInfo']['GPSTimeStamp'])
            metadata['creation_date'] = datetime\
                .strptime(f"{gps_date} {gps_time}".replace('\x00', '').replace('-', ':'), '%Y:%m:%d %H:%M:%S')\
                .strftime('%Y-%m-%dT%H:%M:%SZ')
        except KeyError:
            pass
    elif 'DateTimeOriginal' in exif:
        # There is no timezone information on this date
        metadata['creation_date'] = datetime\
            .strptime(exif['DateTimeOriginal'].replace('\x00', '').replace('-', ':'), '%Y:%m:%d %H:%M:%S')\
            .strftime('%Y-%m-%dT%H:%M:%SZ')

    return metadata
