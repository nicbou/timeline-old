from gpxpy.gpx import GPXTrackPoint as Point
import gpxpy as gpxpy
from rest_framework.renderers import BaseRenderer

from source.utils.datetime import json_to_datetime


class GpxRenderer(BaseRenderer):
    """
    Render GPX file from entries
    """
    media_type = "application/gpx+xml"
    format = "gpx"
    charset = "utf-8"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        gpx = gpxpy.gpx.GPX()
        gpx_track = gpxpy.gpx.GPXTrack()
        gpx.tracks.append(gpx_track)
        gpx_segment = gpxpy.gpx.GPXTrackSegment()
        gpx_track.segments.append(gpx_segment)

        for entry in data:
            location = entry['extra_attributes'].get('location')
            if location and location.get('latitude') is not None and location.get('longitude') is not None:
                gpx_segment.points.append(Point(
                    location['latitude'],
                    location['longitude'],
                    time=json_to_datetime(entry['date_on_timeline']),
                    elevation=location.get('elevation'),
                    name=entry['title'] or None,
                    comment=entry['description'] or None,
                ))

        return gpx.to_xml()
