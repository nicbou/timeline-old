from .models import BackupSource
from .serializers import BackupSourceSerializer
from django.core.management import call_command
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.response import Response
import logging
import os

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
        call_command(
            'copy_ssh_keys',
            user=data.get('user'),
            password=data.pop('password'),
            host=data.get('host'),
            port=data.get('port'),
        )

        return super().perform_create(serializer)


class BackupViewSet(viewsets.ViewSet):
    """
    List and manage Backups on the filesystem. A Backup is a set of files generated when a Source is backed up.
    """
    def get_backups_for_source(self, source):
        backups = []
        backup_paths = sorted(next(os.walk(source.backups_root))[1], reverse=True)
        for backup_path in backup_paths:
            try:
                backups.append({
                    'date': source.datetime_from_backup_path(backup_path),
                    'path': os.path.join(source.backups_root, backup_path),
                })
            except ValueError:
                pass  # Not a backup directory
        return backups

    def list(self, request):
        backups_by_source_key = {
            source.key: self.get_backups_for_source(source)
            for source in BackupSource.objects.all().order_by('key')
        }
        return Response(backups_by_source_key)

    def retrieve(self, request, pk=None):
        return Response(self.get_backups_for_source(BackupSource.objects.get(pk=pk)))
