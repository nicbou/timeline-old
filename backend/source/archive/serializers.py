from rest_framework import serializers

from archive.models import JsonArchive, GpxArchive, N26CsvArchive, TelegramArchive
from archive.models.google_takeout import GoogleTakeoutArchive
from archive.models.twitter import TwitterArchive


class GoogleTakeoutArchiveSerializer(serializers.HyperlinkedModelSerializer):
    key = serializers.CharField()

    class Meta:
        model = GoogleTakeoutArchive
        fields = '__all__'


class TwitterArchiveSerializer(serializers.HyperlinkedModelSerializer):
    key = serializers.CharField()

    class Meta:
        model = TwitterArchive
        fields = '__all__'


class JsonArchiveSerializer(serializers.HyperlinkedModelSerializer):
    key = serializers.CharField()

    class Meta:
        model = JsonArchive
        fields = '__all__'


class GpxArchiveSerializer(serializers.HyperlinkedModelSerializer):
    key = serializers.CharField()

    class Meta:
        model = GpxArchive
        fields = '__all__'


class N26CsvArchiveSerializer(serializers.HyperlinkedModelSerializer):
    key = serializers.CharField()

    class Meta:
        model = N26CsvArchive
        fields = '__all__'


class TelegramArchiveSerializer(serializers.HyperlinkedModelSerializer):
    key = serializers.CharField()

    class Meta:
        model = TelegramArchive
        fields = '__all__'
