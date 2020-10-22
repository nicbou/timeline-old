from collections import namedtuple
from datetime import datetime
from django.conf import settings
from django.db import models
from pathlib import Path
from typing import Generator
import os


class Backup:
    """
    Describes set of files created after a single backup run
    """
    source: 'BackupSource' = None
    date: datetime = None
    date_format = '%Y-%m-%dT%H.%M.%SZ'  # Using colons would break things
    latest_backup_dirname = 'latest'

    def __init__(self, source: 'BackupSource', date: datetime=None, path: Path=None):
        self.source = source
        if date:
            self.date = date
        elif path:
            try:
                self.date = datetime.strptime(path.name, "%Y-%m-%dT%H.%M.%SZ")
            except ValueError:
                raise ValueError("Invalid path specified. Not a backup directory.")

    @property
    def root_path(self) -> Path:
        if self.date:
            return self.source.backups_root.resolve() / self.date.strftime(self.date_format)
        else:
            return self.source.backups_root.resolve() / self.latest_backup_dirname

    @property
    def log_path(self) -> Path:
        return self.root_path / 'rsync.log'

    @property
    def files_path(self) -> Path:
        return self.root_path / 'files'


class BackupSource(models.Model):
    user = models.CharField(max_length=80, blank=False)
    host = models.CharField(max_length=255, blank=False)
    port = models.PositiveSmallIntegerField(default=22)
    path = models.TextField(blank=False)
    key = models.CharField(max_length=80, blank=False, unique=True)

    @property
    def backups_root(self) -> Path:
        return settings.BACKUPS_ROOT.resolve() / self.key

    @property
    def latest_backup(self) -> Backup:
        return Backup(source=self, date=None)

    @property
    def backups(self) -> Generator[Backup, None, None]:
        try:
            backup_dirs = sorted(self.backups_root.iterdir(), reverse=True)
        except FileNotFoundError:
            return

        for backup_dir in backup_dirs:
            if not backup_dir.is_dir():
                continue
            try:
                yield Backup(source=self, path=backup_dir)
            except ValueError:
                continue

    def __str__(self):
        return f"{self.key} ({self.user}@{self.host}:{self.port}, {self.path})"