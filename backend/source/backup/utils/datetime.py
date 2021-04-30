from datetime import datetime

import pytz


def parse_exif_date(date_str: str) -> datetime:
    # Official format: YYYY:MM:DD HH:MM:SS
    # Also seen: YYYY-MM-DD HH:MM:SS and YYYY-MM-DDTHH:MM:SS+ZZZZ
    return datetime.strptime(
        date_str.replace('-', ':').replace('T', ' ')[:19],
        '%Y:%m:%d %H:%M:%S'
    )


def datetime_to_json(date: datetime) -> str:
    return date.strftime('%Y-%m-%dT%H:%M:%SZ')


def json_to_datetime(date_str: str) -> datetime:
    return pytz.utc.localize(datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ"))