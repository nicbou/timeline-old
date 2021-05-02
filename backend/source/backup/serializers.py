from rest_framework import serializers

from .models import FileSystemSource
from .models.hackernews import HackerNewsSource
from .models.reddit import RedditSource
from .models.rss import RssSource
from .models.rsync import RsyncSource, RsyncDestination
from .models.twitter import TwitterSource


class RsyncSourceSerializer(serializers.HyperlinkedModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = RsyncSource
        fields = ['key', 'user', 'host', 'port', 'path', 'key_exchange_method', 'max_backups', 'password']


class RsyncDestinationSerializer(serializers.HyperlinkedModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = RsyncDestination
        fields = ['key', 'user', 'host', 'port', 'path', 'key_exchange_method', 'password']


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


class RssSourceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = RssSource
        fields = '__all__'


class FileSystemSourceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = FileSystemSource
        fields = '__all__'
