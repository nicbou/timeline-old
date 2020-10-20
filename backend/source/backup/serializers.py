from .models import BackupSource
from rest_framework import serializers


class BackupSourceSerializer(serializers.HyperlinkedModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    class Meta:
        model = BackupSource
        fields = ['id', 'user', 'host', 'port', 'path', 'password']