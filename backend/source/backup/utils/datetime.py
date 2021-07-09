from datetime import datetime

import pytz


def parse_exif_date(date_str: str) -> datetime:
    # Official format: YYYY:MM:DD HH:MM:SS
    # Also seen: YYYY-MM-DD HH:MM:SS and YYYY-MM-DDTHH:MM:SS+ZZZZ
    return datetime.strptime(
        date_str.replace('\x00', '').replace('-', ':').replace('T', ' ')[:19],
        '%Y:%m:%d %H:%M:%S'
    )


def datetime_to_json(date: datetime) -> str:
    return date.strftime('%Y-%m-%dT%H:%M:%SZ')


def json_to_datetime(date_str: str) -> datetime:
    try:
        parsed_date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        # Date with milliseconds
        parsed_date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    return pytz.utc.localize(parsed_date)