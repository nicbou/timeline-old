import logging
from collections import defaultdict
from datetime import datetime, date
from typing import Generator

import pytz
from icalendar import Calendar

from archive.models.base import FileArchive
from source.utils.datetime import datetime_to_json
from timeline.models import Entry

logger = logging.getLogger(__name__)


class ICalendarArchive(FileArchive):
    @staticmethod
    def normalize_date(date_obj: datetime):
        if type(date_obj) == date:
            # TODO: What time should an all-day event have?
            date_obj = pytz.utc.localize(datetime(year=date_obj.year, month=date_obj.month, day=date_obj.day, hour=12))
        return date_obj

    def extract_entries(self) -> Generator[Entry, None, None]:
        for ics_file in self.get_archive_files():
            with open(ics_file, 'r') as file:
                calendar = Calendar.from_ical(file.read())
                for event in calendar.walk('VEVENT'):
                    event_metadata = defaultdict(dict)
                    event_metadata['event']['start_date'] = datetime_to_json(self.normalize_date(event['DTSTART'].dt))

                    if event.get('DTEND'):
                        event_metadata['event']['end_date'] = datetime_to_json(self.normalize_date(event['DTEND'].dt))

                    if event.get('DTSTAMP'):
                        event_metadata['event']['creation_date'] = datetime_to_json(self.normalize_date(event['DTSTAMP'].dt))

                    if event.get('LOCATION'):
                        event_metadata['location']['name'] = event['LOCATION']

                    yield Entry(
                        source=self.entry_source,
                        schema='event',
                        title=str(event.get('SUMMARY', '')),
                        description=str(event.get('DESCRIPTION', '')),
                        date_on_timeline=self.normalize_date(event['DTSTART'].dt),
                        extra_attributes=dict(event_metadata),
                    )