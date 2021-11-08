import logging
from typing import Generator

import gpxpy as gpxpy

from archive.models.base import FileArchive
from backup.utils.datetime import datetime_to_json
from timeline.models import Entry

logger = logging.getLogger(__name__)


class GpxArchive(FileArchive):
    """
    A single GPX file
    """
    def entry_from_point(self, point) -> Entry:
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
            date_on_timeline=datetime_to_json(point.time)
        )

    def extract_entries(self) -> Generator[Entry, None, None]:
        for gpx_file in self.get_archive_files():
            gpx = gpxpy.parse(gpx_file)
            for track in gpx.tracks:
                for segment in track.segments:
                    for point in segment.points:
                        yield self.entry_from_point(point)

            for route in gpx.routes:
                for point in route.points:
                    yield self.entry_from_point(point)

            for point in gpx.waypoints:
                yield self.entry_from_point(point)
