from .management.commands.copy_ssh_keys import SSHTimeoutError, SSHCredentialsError
from .models import FileSystemSource
from .models.rsync import RsyncSource
from .models.twitter import TwitterSource
from .models.reddit import RedditSource
from .models.hackernews import HackerNewsSource
from .models.rss import RssSource
from .serializers import RsyncSourceSerializer, TwitterSourceSerializer, RedditSourceSerializer, \
    HackerNewsSourceSerializer, RssSourceSerializer, FileSystemSourceSerializer
from django.core.management import call_command
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.exceptions import APIException, AuthenticationFailed
from rest_framework.response import Response
import logging

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
            call_command(
                'copy_ssh_keys',
                user=data.get('user'),
                password=data.pop('password'),
                host=data.get('host'),
                port=data.get('port'),
            )
        except SSHCredentialsError:
            raise AuthenticationFailed('Could not fetch SSH keys. The credentials are incorrect.')
        except SSHTimeoutError:
            raise APIException('Could not fetch SSH keys. The operation timed out. Are the host and port correct?')

        return super().perform_create(serializer)


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
