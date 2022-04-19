from django.db import transaction
from rest_framework import serializers

from archive.models import JsonArchive, GpxArchive, N26CsvArchive, TelegramArchive, FacebookArchive, ICalendarArchive
from archive.models.base import ArchiveFile
from archive.models.google_takeout import GoogleTakeoutArchive
from archive.models.twitter import TwitterArchive
from source.serializers import BaseSourceSerializer


class ArchiveFileSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField('get_file_url')

    def get_file_url(self, archive_file):
        return archive_file.archive_file.url

    class Meta:
        model = ArchiveFile
        fields = ('id', 'url')


class ArchiveFileRelatedField(serializers.RelatedField):
    def to_representation(self, archive_file: ArchiveFile):
        return {
            'url': archive_file.archive_file.url,
            'id': archive_file.id,
        }

    def to_internal_value(self, data) -> ArchiveFile:
        return ArchiveFile(archive_file=data)


class BaseArchiveSerializer(BaseSourceSerializer):
    archive_files = ArchiveFileRelatedField(many=True, queryset=ArchiveFile.objects.all())

    def create(self, validated_data):
        with transaction.atomic():
            archive_files_uploads = validated_data.pop('archive_files')
            archive = self.Meta.model.objects.create(**validated_data)
            for archive_file in archive_files_uploads:
                archive_file.archive = archive
                archive_file.save()
        return archive

    def update(self, instance, validated_data):
        with transaction.atomic():
            archive_files_uploads = validated_data.pop('archive_files')
            for archive_file in archive_files_uploads:
                archive_file.archive = instance
                archive_file.save()
        return super().update(instance, validated_data)


class GoogleTakeoutArchiveSerializer(BaseArchiveSerializer):
    class Meta:
        model = GoogleTakeoutArchive
        fields = '__all__'


class TwitterArchiveSerializer(BaseArchiveSerializer):
    class Meta:
        model = TwitterArchive
        fields = '__all__'


class JsonArchiveSerializer(BaseArchiveSerializer):
    class Meta:
        model = JsonArchive
        fields = '__all__'


class GpxArchiveSerializer(BaseArchiveSerializer):
    class Meta:
        model = GpxArchive
        fields = '__all__'


class N26CsvArchiveSerializer(BaseArchiveSerializer):
    class Meta:
        model = N26CsvArchive
        fields = '__all__'


class TelegramArchiveSerializer(BaseArchiveSerializer):
    class Meta:
        model = TelegramArchive
        fields = '__all__'


class FacebookArchiveSerializer(BaseArchiveSerializer):
    class Meta:
        model = FacebookArchive
        fields = '__all__'


class ICalendarArchiveSerializer(BaseArchiveSerializer):
    class Meta:
        model = ICalendarArchive
        fields = '__all__'