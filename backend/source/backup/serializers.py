from .models import BackupSource, TwitterSource, RedditSource, HackerNewsSource
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


class RedditSourceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = RedditSource
        fields = '__all__'


class HackerNewsSourceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = HackerNewsSource
        fields = '__all__'
