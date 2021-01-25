import json
import logging
from datetime import datetime
import pytz

from archive.models import Archive
from timeline.models import Entry


logger = logging.getLogger(__name__)


def e7_to_decimal(e7_coordinate: int) -> float:
    return float(e7_coordinate) / 10000000


def geolocation_entry(date_on_timeline: datetime, latitude: float, longitude: float, altitude: float = None,
                      archive: 'Archive' = None, title: str = '') -> Entry:
    return Entry(
        title=title or '',
        description='',
        extra_attributes={
            'location': {
                'latitude': latitude,
                'longitude': longitude,
                'altitude': altitude,
            },
            'source': archive.entry_source,
        },
        date_on_timeline=date_on_timeline,
    )


class GoogleTakeoutArchive(Archive):
    def process(self):
        try:
            self.delete_extracted_files()
            self.delete_entries()
            self.extract_files()
            self.process_location_history()
        except:
            logger.exception(f'Failed to process archive "{self.key}"')
            raise
        finally:
            self.delete_extracted_files()

        self.date_processed = datetime.now(pytz.UTC)
        self.save()

    def process_location_history(self):
        json_files = list(self.files_path.glob('**/Semantic Location History/**/*.json'))
        logger.info(f'Processing location history in "{self.key}" archive ({str(self.root_path)}). '
                    f'{len(json_files)} files found.')

        total_entries_created = 0
        for json_file in json_files:
            logger.info(f'Processing entries in {str(json_file)}')
            with json_file.open(encoding='utf-8') as json_file_handle:
                json_entries = json.load(json_file_handle)['timelineObjects']

            db_entries = []
            for entry in json_entries:
                if 'activitySegment' in entry:
                    if 'latitudeE7' in entry['activitySegment']['startLocation']:
                        db_entries.append(
                            geolocation_entry(
                                date_on_timeline=datetime.fromtimestamp(
                                    int(entry['activitySegment']['duration']['startTimestampMs']) / 1000, tz=pytz.UTC
                                ),
                                latitude=e7_to_decimal(entry['activitySegment']['startLocation']['latitudeE7']),
                                longitude=e7_to_decimal(entry['activitySegment']['startLocation']['longitudeE7']),
                                archive=self,
                            )
                        )

                    if 'latitudeE7' in entry['activitySegment']['endLocation']:
                        db_entries.append(
                            geolocation_entry(
                                date_on_timeline=datetime.fromtimestamp(
                                    int(entry['activitySegment']['duration']['endTimestampMs']) / 1000, tz=pytz.UTC
                                ),
                                latitude=e7_to_decimal(entry['activitySegment']['endLocation']['latitudeE7']),
                                longitude=e7_to_decimal(entry['activitySegment']['endLocation']['longitudeE7']),
                                archive=self,
                            )
                        )

                if 'placeVisit' in entry:
                    db_entries.append(
                        geolocation_entry(
                            title=(
                                entry['placeVisit']['location'].get('name')
                                or entry['placeVisit']['otherCandidateLocations'][0].get('name')
                            ),
                            date_on_timeline=datetime.fromtimestamp(
                                int(entry['placeVisit']['duration']['endTimestampMs']) / 1000, tz=pytz.UTC
                            ),
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
                    )

            logger.info(f"Adding {len(db_entries)} entries found in {str(json_file)}")
            total_entries_created += len(Entry.objects.bulk_create(db_entries))
        logging.info(f'Done processing "{self.key}" archive. {total_entries_created} entries created.')

        return total_entries_created
