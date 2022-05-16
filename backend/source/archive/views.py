from rest_framework import viewsets, permissions

from archive.models import JsonArchive, GpxArchive, N26CsvArchive, TelegramArchive, FacebookArchive, ArchiveFile, \
    ICalendarArchive, RedditArchive
from archive.models.google_takeout import GoogleTakeoutArchive
from archive.models.twitter import TwitterArchive
from archive.serializers import GoogleTakeoutArchiveSerializer, TwitterArchiveSerializer, JsonArchiveSerializer, \
    GpxArchiveSerializer, N26CsvArchiveSerializer, TelegramArchiveSerializer, FacebookArchiveSerializer, \
    ArchiveFileSerializer, ICalendarArchiveSerializer, RedditArchiveSerializer


class GoogleTakeoutArchiveViewSet(viewsets.ModelViewSet):
    queryset = GoogleTakeoutArchive.objects.all()
    serializer_class = GoogleTakeoutArchiveSerializer
    permission_classes = [permissions.AllowAny]


class TwitterArchiveViewSet(viewsets.ModelViewSet):
    queryset = TwitterArchive.objects.all()
    serializer_class = TwitterArchiveSerializer
    permission_classes = [permissions.AllowAny]


class JsonArchiveViewSet(viewsets.ModelViewSet):
    queryset = JsonArchive.objects.all()
    serializer_class = JsonArchiveSerializer
    permission_classes = [permissions.AllowAny]


class GpxArchiveViewSet(viewsets.ModelViewSet):
    queryset = GpxArchive.objects.all()
    serializer_class = GpxArchiveSerializer
    permission_classes = [permissions.AllowAny]


class N26CsvArchiveViewSet(viewsets.ModelViewSet):
    queryset = N26CsvArchive.objects.all()
    serializer_class = N26CsvArchiveSerializer
    permission_classes = [permissions.AllowAny]


class TelegramArchiveViewSet(viewsets.ModelViewSet):
    queryset = TelegramArchive.objects.all()
    serializer_class = TelegramArchiveSerializer
    permission_classes = [permissions.AllowAny]


class FacebookArchiveViewSet(viewsets.ModelViewSet):
    queryset = FacebookArchive.objects.all()
    serializer_class = FacebookArchiveSerializer
    permission_classes = [permissions.AllowAny]


class ICalendarArchiveViewSet(viewsets.ModelViewSet):
    queryset = ICalendarArchive.objects.all()
    serializer_class = ICalendarArchiveSerializer
    permission_classes = [permissions.AllowAny]


class RedditArchiveViewSet(viewsets.ModelViewSet):
    queryset = RedditArchive.objects.all()
    serializer_class = RedditArchiveSerializer
    permission_classes = [permissions.AllowAny]


class ArchiveFileViewSet(viewsets.ModelViewSet):
    queryset = ArchiveFile.objects.all()
    serializer_class = ArchiveFileSerializer
    permission_classes = [permissions.AllowAny]
    http_method_names = ['get', 'list', 'delete']