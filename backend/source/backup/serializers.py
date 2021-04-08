from .models import FileSystemSource
from .models.rsync import RsyncSource, RsyncDestination
from .models.twitter import TwitterSource
from .models.reddit import RedditSource
from .models.hackernews import HackerNewsSource
from .models.rss import RssSource
from rest_framework import serializers


class RsyncSourceSerializer(serializers.HyperlinkedModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = RsyncSource
        fields = ['id', 'key', 'user', 'host', 'port', 'path', 'max_backups', 'password']


class RsyncDestinationSerializer(serializers.HyperlinkedModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = RsyncDestination
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


class RssSourceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = RssSource
        fields = '__all__'


class FileSystemSourceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = FileSystemSource
        fields = '__all__'
