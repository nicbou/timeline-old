from oauth2_provider.contrib.rest_framework import TokenMatchesOASRequirements
from rest_framework import viewsets, permissions

from archive.models import JsonArchive, GpxArchive, N26CsvArchive, TelegramArchive, FacebookArchive, ArchiveFile, \
    ICalendarArchive, RedditArchive
from archive.models.google_takeout import GoogleTakeoutArchive
from archive.models.twitter import TwitterArchive
from archive.serializers import GoogleTakeoutArchiveSerializer, TwitterArchiveSerializer, JsonArchiveSerializer, \
    GpxArchiveSerializer, N26CsvArchiveSerializer, TelegramArchiveSerializer, FacebookArchiveSerializer, \
    ArchiveFileSerializer, ICalendarArchiveSerializer, RedditArchiveSerializer


class ArchiveModelViewSet(viewsets.ModelViewSet):
    permission_classes = [TokenMatchesOASRequirements]
    required_alternate_scopes = {
        "GET": [["archive:read"]],
        "POST": [["archive:write"]],
        "PUT":  [["archive:write"]],
        "DELETE": [["archive:write"]],
    }


class GoogleTakeoutArchiveViewSet(ArchiveModelViewSet):
    queryset = GoogleTakeoutArchive.objects.all()
    serializer_class = GoogleTakeoutArchiveSerializer


class TwitterArchiveViewSet(ArchiveModelViewSet):
    queryset = TwitterArchive.objects.all()
    serializer_class = TwitterArchiveSerializer


class JsonArchiveViewSet(ArchiveModelViewSet):
    queryset = JsonArchive.objects.all()
    serializer_class = JsonArchiveSerializer


class GpxArchiveViewSet(ArchiveModelViewSet):
    queryset = GpxArchive.objects.all()
    serializer_class = GpxArchiveSerializer


class N26CsvArchiveViewSet(ArchiveModelViewSet):
    queryset = N26CsvArchive.objects.all()
    serializer_class = N26CsvArchiveSerializer


class TelegramArchiveViewSet(ArchiveModelViewSet):
    queryset = TelegramArchive.objects.all()
    serializer_class = TelegramArchiveSerializer


class FacebookArchiveViewSet(ArchiveModelViewSet):
    queryset = FacebookArchive.objects.all()
    serializer_class = FacebookArchiveSerializer


class ICalendarArchiveViewSet(ArchiveModelViewSet):
    queryset = ICalendarArchive.objects.all()
    serializer_class = ICalendarArchiveSerializer


class RedditArchiveViewSet(ArchiveModelViewSet):
    queryset = RedditArchive.objects.all()
    serializer_class = RedditArchiveSerializer


class ArchiveFileViewSet(ArchiveModelViewSet):
    queryset = ArchiveFile.objects.all()
    serializer_class = ArchiveFileSerializer
    http_method_names = ['get', 'list', 'delete']