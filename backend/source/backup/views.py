from .models import FileSystemSource
from .models.rsync import RsyncSource, RsyncDestination
from .models.twitter import TwitterSource
from .models.reddit import RedditSource
from .models.hackernews import HackerNewsSource
from .models.rss import RssSource
from .serializers import RsyncSourceSerializer, TwitterSourceSerializer, RedditSourceSerializer, \
    HackerNewsSourceSerializer, RssSourceSerializer, FileSystemSourceSerializer, RsyncDestinationSerializer
from django.core.management import call_command
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.exceptions import APIException, AuthenticationFailed
from rest_framework.response import Response
import logging

from .utils.ssh import copy_ssh_keys, SSHCredentialsError, SSHTimeoutError

logger = logging.getLogger(__name__)


class RsyncSourceViewSet(viewsets.ModelViewSet):
    """
    List and manage backup Sources. A Source is a remote server from which files are backed up.
    """
    queryset = RsyncSource.objects.all().order_by('key')
    serializer_class = RsyncSourceSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        data = serializer.validated_data
        try:
            logger.info(f"Copying SSH keys to {data['host']}")
            copy_ssh_keys(data['host'], data['port'], data['user'], data['password'])
        except SSHCredentialsError:
            raise AuthenticationFailed('Could not fetch SSH keys. The credentials are incorrect.')
        except SSHTimeoutError:
            raise APIException('Could not fetch SSH keys. The operation timed out. Are the host and port correct?')
        except:
            raise APIException('Could not fetch SSH keys.')

        return super().perform_create(serializer)


class RsyncDestinationViewSet(RsyncSourceViewSet):
    queryset = RsyncDestination.objects.all().order_by('key')
    serializer_class = RsyncDestinationSerializer


class TwitterSourceViewSet(viewsets.ModelViewSet):
    queryset = TwitterSource.objects.all().order_by('twitter_username')
    serializer_class = TwitterSourceSerializer
    permission_classes = [permissions.AllowAny]


class RedditSourceViewSet(viewsets.ModelViewSet):
    queryset = RedditSource.objects.all().order_by('reddit_username')
    serializer_class = RedditSourceSerializer
    permission_classes = [permissions.AllowAny]


class HackerNewsSourceViewSet(viewsets.ModelViewSet):
    queryset = HackerNewsSource.objects.all().order_by('hackernews_username')
    serializer_class = HackerNewsSourceSerializer
    permission_classes = [permissions.AllowAny]


class RssSourceViewSet(viewsets.ModelViewSet):
    queryset = RssSource.objects.all()
    serializer_class = RssSourceSerializer
    permission_classes = [permissions.AllowAny]


class FileSystemSourceViewSet(viewsets.ModelViewSet):
    queryset = FileSystemSource.objects.all()
    serializer_class = FileSystemSourceSerializer
    permission_classes = [permissions.AllowAny]
