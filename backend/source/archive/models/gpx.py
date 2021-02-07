import logging
from collections import Generator

import gpxpy as gpxpy

from archive.models.base import BaseArchive
from timeline.models import Entry

logger = logging.getLogger(__name__)


class GpxArchive(BaseArchive):
    """
    A single GPX file
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

    def extract_entries(self) -> Generator[Entry, None, None]:
        gpx = gpxpy.parse(self.archive_file.file)
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    yield self.entry_from_point(point)

        for route in gpx.routes:
            for point in route.points:
                yield self.entry_from_point(point)

        for point in gpx.waypoints:
            yield self.entry_from_point(point)
