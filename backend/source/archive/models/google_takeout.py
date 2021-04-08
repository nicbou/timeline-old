import json
import logging
from collections import Generator
from datetime import datetime
from pathlib import Path
from typing import Iterable

import pytz

from archive.models.base import BaseArchive, CompressedArchive
from backup.utils.datetime import json_to_datetime
from timeline.models import Entry

logger = logging.getLogger(__name__)


def e7_to_decimal(e7_coordinate: int) -> float:
    return float(e7_coordinate) / 10000000


def millis_str_to_time(timestamp: str) -> datetime:
    return datetime.fromtimestamp(int(timestamp) / 1000, tz=pytz.UTC)


def microseconds_to_time(timestamp: int):
    return datetime.fromtimestamp(int(timestamp) / 1000000, tz=pytz.UTC)


def geolocation_entry(date_on_timeline: datetime, latitude: float, longitude: float, archive: 'BaseArchive',
                      altitude: float = None, accuracy: int = None, title: str = '') -> Entry:
    entry = Entry(
        title=title or '',
        description='',
        schema='activity.location',
        source=archive.entry_source,
        extra_attributes={
            'location': {
                'latitude': latitude,
                'longitude': longitude,
            },
        },
        date_on_timeline=date_on_timeline,
    )

    if altitude is not None:
        entry.extra_attributes['location']['altitude'] = altitude

    if accuracy is not None:
        entry.extra_attributes['location']['accuracy'] = accuracy

    return entry


def browsing_history_entry(date_on_timeline: datetime, archive: 'BaseArchive', url: str, title: str = '') -> Entry:
    return Entry(
        title=title or '',
        description='',
        schema='activity.browsing.website',
        source=archive.entry_source,
        extra_attributes={
            'url': url,
        },
        date_on_timeline=date_on_timeline,
    )


class GoogleTakeoutArchive(CompressedArchive):
    """
    A Google Takeout data export. Can contain all data, or only data from some services
    """
    source_name = 'google'

    def extract_entries(self) -> Generator[Entry, None, None]:
        yield from self.extract_location_history()
        yield from self.extract_browser_history()
        yield from self.extract_search_history()
        yield from self.extract_youtube_history()

    def extract_browser_history(self) -> Generator[Entry, None, None]:
        json_files = list(self.files_path.glob('**/Chrome/BrowserHistory.json'))
        logger.info(f'Processing browser history in "{self.entry_source}". '
                    f'{len(json_files)} files found.')

        for json_file in json_files:
            logger.info(f'Processing browser history entries in {str(json_file)}')
            with json_file.open(encoding='utf-8') as json_file_handle:
                json_entries = json.load(json_file_handle)['Browser History']

            for entry in json_entries:
                if entry['page_transition'] in ('FORM_SUBMIT', 'RELOAD'):
                    continue

                yield browsing_history_entry(
                    title=entry['title'],
                    date_on_timeline=microseconds_to_time(entry['time_usec']),
                    url=entry['url'],
                    archive=self,
                )

    def extract_location_history(self) -> Generator[Entry, None, None]:
        json_files = list(self.files_path.glob('**/Semantic Location History/**/*.json'))
        logger.info(f'Processing location history in "{self.entry_source}". '
                    f'{len(json_files)} files found.')

        for json_file in json_files:
            logger.info(f'Processing location history entries in {str(json_file)}')
            with json_file.open(encoding='utf-8') as json_file_handle:
                json_entries = json.load(json_file_handle)['timelineObjects']

            for entry in json_entries:
                if 'activitySegment' in entry:
                    if 'latitudeE7' in entry['activitySegment']['startLocation']:
                        yield geolocation_entry(
                            date_on_timeline=millis_str_to_time(
                                entry['activitySegment']['duration']['startTimestampMs']),
                            latitude=e7_to_decimal(entry['activitySegment']['startLocation']['latitudeE7']),
                            longitude=e7_to_decimal(entry['activitySegment']['startLocation']['longitudeE7']),
                            archive=self,
                        )

                    if 'latitudeE7' in entry['activitySegment']['endLocation']:
                        yield geolocation_entry(
                            date_on_timeline=millis_str_to_time(
                                entry['activitySegment']['duration']['endTimestampMs']),
                            latitude=e7_to_decimal(entry['activitySegment']['endLocation']['latitudeE7']),
                            longitude=e7_to_decimal(entry['activitySegment']['endLocation']['longitudeE7']),
                            archive=self,
                        )

                    if 'simplifiedRawPath' in entry['activitySegment']:
                        for point in entry['activitySegment']['simplifiedRawPath'].get('points', []):
                            yield geolocation_entry(
                                date_on_timeline=millis_str_to_time(point['timestampMs']),
                                latitude=e7_to_decimal(point['latE7']),
                                longitude=e7_to_decimal(point['lngE7']),
                                accuracy=point['accuracyMeters'],
                                archive=self,
                            )

                if 'placeVisit' in entry:
                    yield geolocation_entry(
                        title=(
                            entry['placeVisit']['location'].get('name')
                            or entry['placeVisit']['otherCandidateLocations'][0].get('name')
                        ),
                        date_on_timeline=millis_str_to_time(entry['placeVisit']['duration']['endTimestampMs']),
                        latitude=e7_to_decimal(
                            entry['placeVisit']['location'].get('latitudeE7')
                            or entry['placeVisit']['otherCandidateLocations'][0].get('latitudeE7')
                        ),
                        longitude=e7_to_decimal(
                            entry['placeVisit']['location'].get('longitudeE7')
                            or entry['placeVisit']['otherCandidateLocations'][0].get('longitudeE7')
                        ),
                        archive=self,
                    )

    def extract_search_history(self) -> Generator[Entry, None, None]:
        yield from self.extract_history_entries(
            json_files=(
                self.files_path / 'Takeout/My Activity/Search/My Activity.json',
                self.files_path / 'Takeout/My Activity/Image Search/My Activity.json',
                self.files_path / 'Takeout/My Activity/Gmail/My Activity.json',
                self.files_path / 'Takeout/My Activity/Finance/My Activity.json',
                self.files_path / 'Takeout/My Activity/Drive/My Activity.json',
            ),
            schema='activity.browsing.search',
            prefix='Searched for ',
        )

    def extract_youtube_history(self) -> Generator[Entry, None, None]:
        yield from self.extract_history_entries(
            json_files=(self.files_path / 'Takeout/My Activity/YouTube/My Activity.json', ),
            schema='activity.browsing.watch',
            prefix='Watched ',
        )

    def extract_history_entries(self, json_files: Iterable[Path], schema: str,
                                prefix: str) -> Generator[Entry, None, None]:
        for json_file in json_files:
            logger.info(f'Processing activity in "{str(json_file)}"')
            for entry in json.load(json_file.open('r')):
                if entry['title'].startswith(prefix):
                    try:
                        time = datetime.strptime(entry['time'], '%Y-%m-%dT%H:%M:%S.%fZ')
                    except ValueError:
                        time = json_to_datetime(entry['time'])

                    extra_attributes = {}
                    if entry.get('titleUrl'):
                        extra_attributes['url'] = entry['titleUrl']

                    try:
                        yield Entry(
                            title=entry['title'].replace(prefix, '', 1),
                            description='',
                            source=self.entry_source,
                            schema=schema,
                            date_on_timeline=pytz.utc.localize(time),
                            extra_attributes=extra_attributes
                        )
                    except:
                        logging.exception(f"Could not parse entry: {entry}")
                        raise
