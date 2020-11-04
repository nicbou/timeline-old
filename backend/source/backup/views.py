from .management.commands.copy_ssh_keys import SSHTimeoutError, SSHCredentialsError
from .models import BackupSource, TwitterSource, RedditSource
from .serializers import BackupSourceSerializer, TwitterSourceSerializer, RedditSourceSerializer
from django.core.management import call_command
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.exceptions import APIException, AuthenticationFailed
from rest_framework.response import Response
import logging

logger = logging.getLogger(__name__)


class BackupSourceViewSet(viewsets.ModelViewSet):
    """
    List and manage backup Sources. A Source is a remote server from which files are backed up.
    """
    queryset = BackupSource.objects.all().order_by('key')
    serializer_class = BackupSourceSerializer
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


class BackupViewSet(viewsets.ViewSet):
    """
    List and manage Backups on the filesystem. A Backup is a set of files generated when a Source is backed up.
    """
    def get_backups_for_source(self, source):
        return [
            {
                'date': backup.date,
                'paths': {
                    'root': str(backup.root_path.resolve()),
                    'files': str(backup.files_path.resolve()),
                    'log': str(backup.log_path.resolve()),
                },
            }
            for backup in source.backups
        ]

    def list(self, request):
        backups_by_source_key = {
            source.key: self.get_backups_for_source(source)
            for source in BackupSource.objects.all().order_by('key')
        }
        return Response(backups_by_source_key)

    def retrieve(self, request, pk=None):
        return Response(self.get_backups_for_source(BackupSource.objects.get(pk=pk)))


class TwitterSourceViewSet(viewsets.ModelViewSet):
    queryset = TwitterSource.objects.all().order_by('twitter_username')
    serializer_class = TwitterSourceSerializer
    permission_classes = [permissions.AllowAny]


class RedditSourceViewSet(viewsets.ModelViewSet):
    queryset = RedditSource.objects.all().order_by('reddit_username')
    serializer_class = RedditSourceSerializer
    permission_classes = [permissions.AllowAny]