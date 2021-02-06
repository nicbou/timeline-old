import json
import logging
from datetime import datetime
from typing import Tuple

import gpxpy as gpxpy
import pytz
from django.db import transaction

from archive.models.base import BaseArchive
from timeline.models import Entry
from timeline.serializers import EntrySerializer

logger = logging.getLogger(__name__)


class GpxArchive(BaseArchive):
    """
    A list of JSON entries, as returned by the API
    """
    source_name = 'gpx'

    def entry_from_point(self, point):
        return Entry(
            schema='activity.location',
            source=self.entry_source,
            title=getattr(point, 'name') or '',
            description=getattr(point, 'description') or getattr(point, 'comment') or '',
            extra_attributes={
                'location': {
                    'latitude': point.latitude,
                    'longitude': point.longitude,
                    'altitude': point.elevation,
                },
            },
            date_on_timeline=point.time.strftime('%Y-%m-%dT%H:%M:%SZ')
        )

    def process(self) -> Tuple[int, int]:
        total_entries_created = 0
        try:
            with transaction.atomic():
                self.delete_entries()
                gpx = gpxpy.parse(self.archive_file.file)
                db_entries = []
                for track in gpx.tracks:
                    for segment in track.segments:
                        db_entries.extend([self.entry_from_point(point) for point in segment.points])

                for route in gpx.routes:
                    db_entries.extend([self.entry_from_point(point) for point in route.points])

                db_entries.extend([self.entry_from_point(point) for point in gpx.waypoints])

                total_entries_created += len(Entry.objects.bulk_create(db_entries))
                self.date_processed = datetime.now(pytz.UTC)
                self.save()
        except:
            logger.exception(f'Failed to process archive "{self.key}"')
            raise
        finally:
            self.delete_extracted_files()

        logging.info(f'Done processing "{self.key}" archive. {total_entries_created} entries created.')
        return total_entries_created, 0
