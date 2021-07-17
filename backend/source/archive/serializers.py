from django.db import transaction
from rest_framework import serializers

from archive.models import JsonArchive, GpxArchive, N26CsvArchive, TelegramArchive, FacebookArchive
from archive.models.base import ArchiveFile
from archive.models.google_takeout import GoogleTakeoutArchive
from archive.models.twitter import TwitterArchive


class ArchiveFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArchiveFile
        fields = '__all__'


class ArchiveFileRelatedField(serializers.RelatedField):
    def to_representation(self, archive_file: ArchiveFile):
        return archive_file.archive_file.path

    def to_internal_value(self, data) -> ArchiveFile:
        return ArchiveFile(archive_file=data)


class BaseArchiveSerializer(serializers.HyperlinkedModelSerializer):
    key = serializers.CharField()
    archive_files = ArchiveFileRelatedField(many=True, queryset=ArchiveFile.objects.all())

    def create(self, validated_data):
        with transaction.atomic():
            archive_files_uploads = validated_data.pop('archive_files')
            archive = self.Meta.model.objects.create(**validated_data)
            for archive_file in archive_files_uploads:
                archive_file.archive = archive
                archive_file.save()
        return archive


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