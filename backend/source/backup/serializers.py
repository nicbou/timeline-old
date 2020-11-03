from .models import BackupSource, TwitterSource
from rest_framework import serializers


class BackupSourceSerializer(serializers.HyperlinkedModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = BackupSource
        fields = ['id', 'key', 'user', 'host', 'port', 'path', 'password']


class TwitterSourceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TwitterSource
        fields = '__all__'
