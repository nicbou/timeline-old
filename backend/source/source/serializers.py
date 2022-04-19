from rest_framework import serializers

from .models import FileSystemSource
from .models.git import GitSource
from .models.hackernews import HackerNewsSource
from .models.reddit import RedditSource
from .models.rss import RssSource
from .models.rsync import RsyncSource
from .models.twitter import TwitterSource


class BaseSourceSerializer(serializers.HyperlinkedModelSerializer):
    key = serializers.CharField()


class RsyncSourceSerializer(BaseSourceSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = RsyncSource
        fields = '__all__'


class TwitterSourceSerializer(BaseSourceSerializer):
    class Meta:
        model = TwitterSource
        fields = '__all__'


class RedditSourceSerializer(BaseSourceSerializer):
    class Meta:
        model = RedditSource
        fields = '__all__'


class HackerNewsSourceSerializer(BaseSourceSerializer):
    class Meta:
        model = HackerNewsSource
        fields = '__all__'


class RssSourceSerializer(BaseSourceSerializer):
    class Meta:
        model = RssSource
        fields = '__all__'


class FileSystemSourceSerializer(BaseSourceSerializer):
    class Meta:
        model = FileSystemSource
        fields = '__all__'


class GitSourceSerializer(BaseSourceSerializer):
    class Meta:
        model = GitSource
        fields = '__all__'
