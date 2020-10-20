from .models import BackupSource
from rest_framework import serializers


class BackupSourceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = BackupSource
        fields = ['user', 'host', 'port', 'path']