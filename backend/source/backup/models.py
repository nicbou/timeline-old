from datetime import datetime
from django.conf import settings
from django.db import models
import os


class BackupSource(models.Model):
    user = models.CharField(max_length=80, blank=False)
    host = models.CharField(max_length=255, blank=False)
    port = models.PositiveSmallIntegerField(default=22)
    path = models.TextField(blank=False)
    key = models.CharField(max_length=80, blank=False, unique=True)

    @property
    def backups_root(self):
        return os.path.abspath(os.path.join(settings.BACKUPS_ROOT, self.key))

    @property
    def latest_backup_path(self):
        return os.path.join(self.backups_root, 'latest')

    def backup_path_from_datetime(self, date):
        return os.path.join(self.backups_root, date.strftime("%Y-%m-%dT%H.%M.%SZ"))

    def datetime_from_backup_path(self, path):
        return datetime.strptime(os.path.basename(path), "%Y-%m-%dT%H.%M.%SZ")

    def __str__(self):
        return f"{self.key} ({self.user}@{self.host}:{self.port}, {self.path})"