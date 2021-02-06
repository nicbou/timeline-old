from rest_framework import serializers

from archive.models import JsonArchive, GpxArchive
from archive.models.google_takeout import GoogleTakeoutArchive
from archive.models.twitter import TwitterArchive


class GoogleTakeoutArchiveSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = GoogleTakeoutArchive
        fields = ['key', 'description', 'date_processed', 'archive_file']


class TwitterArchiveSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TwitterArchive
        fields = ['key', 'description', 'date_processed', 'archive_file']


class JsonArchiveSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = JsonArchive
        fields = ['key', 'description', 'date_processed', 'archive_file']


class GpxArchiveSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = GpxArchive
        fields = ['key', 'description', 'date_processed', 'archive_file']
