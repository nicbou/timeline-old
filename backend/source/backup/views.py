import logging

from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.exceptions import APIException, AuthenticationFailed

from .models import FileSystemSource
from .models.git import GitSource
from .models.hackernews import HackerNewsSource
from .models.reddit import RedditSource
from .models.rss import RssSource
from .models.rsync import RsyncSource
from .models.twitter import TwitterSource
from .serializers import RsyncSourceSerializer, TwitterSourceSerializer, RedditSourceSerializer, \
    HackerNewsSourceSerializer, RssSourceSerializer, FileSystemSourceSerializer, \
    GitSourceSerializer
from .utils.ssh import copy_ssh_keys, SSHCredentialsError, SSHTimeoutError

logger = logging.getLogger(__name__)


class BaseSourceViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]


class RsyncSourceViewSet(BaseSourceViewSet):
    queryset = RsyncSource.objects.all()
    serializer_class = RsyncSourceSerializer

    @staticmethod
    def copy_ssh_keys(serializer):
        data = serializer.validated_data
        try:
            logger.info(f"Copying SSH keys to {data['host']}")
            copy_ssh_keys(data['host'], data['port'], data['user'], data['password'], data['key_exchange_method'])
        except SSHCredentialsError:
            raise AuthenticationFailed('Could not fetch SSH keys. The credentials are incorrect.')
        except SSHTimeoutError:
            raise APIException('Could not fetch SSH keys. The operation timed out. Are the host and port correct?')
        except:
            raise APIException('Could not fetch SSH keys.')

    def perform_create(self, serializer):
        self.copy_ssh_keys(serializer)
        serializer.validated_data.pop('password')
        return super().perform_create(serializer)

    def perform_update(self, serializer):
        self.copy_ssh_keys(serializer)
        serializer.validated_data.pop('password')
        return super().perform_update(serializer)


class TwitterSourceViewSet(BaseSourceViewSet):
    queryset = TwitterSource.objects.all().order_by('twitter_username')
    serializer_class = TwitterSourceSerializer


class RedditSourceViewSet(BaseSourceViewSet):
    queryset = RedditSource.objects.all().order_by('reddit_username')
    serializer_class = RedditSourceSerializer


class HackerNewsSourceViewSet(BaseSourceViewSet):
    queryset = HackerNewsSource.objects.all().order_by('hackernews_username')
    serializer_class = HackerNewsSourceSerializer


class RssSourceViewSet(BaseSourceViewSet):
    queryset = RssSource.objects.all()
    serializer_class = RssSourceSerializer


class FileSystemSourceViewSet(BaseSourceViewSet):
    queryset = FileSystemSource.objects.all()
    serializer_class = FileSystemSourceSerializer


class GitSourceViewSet(BaseSourceViewSet):
    queryset = GitSource.objects.all()
    serializer_class = GitSourceSerializer
