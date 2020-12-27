from datetime import datetime
from django.conf import settings
from django.db import models
from pathlib import Path
from typing import Generator


class Backup:
    """Describes set of files created after a single backup run"""

    source = None
    date = None
    date_format = '%Y-%m-%dT%H.%M.%SZ'  # Using colons would break things
    latest_backup_dirname = 'latest'

    def __init__(self, source: 'BackupSource', date: datetime = None, path: Path = None):
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
            return self.source.backups_root / self.date.strftime(self.date_format)
        else:
            return self.source.backups_root / self.latest_backup_dirname

    @property
    def log_path(self) -> Path:
        return self.root_path / 'rsync.log'

    @property
    def files_path(self) -> Path:
        return self.root_path / 'files'

    def changed_files(self) -> Generator[Path, None, None]:
        for line in self.log_path.open('r').readlines():
            is_file = line[1] == 'f'
            has_content_changed = line[0] == '>' and not (line[3] == line[4] == '.')
            if is_file and has_content_changed:
                yield self.files_path / line.split(' ', 1)[1].strip()

    def __str__(self):
        return f"{self.source.key} ({self.date})"


class BackupSource(models.Model):
    user = models.CharField(max_length=80, blank=False)
    host = models.CharField(max_length=255, blank=False)
    port = models.PositiveSmallIntegerField(default=22)
    path = models.TextField(blank=False)
    key = models.CharField(max_length=80, blank=False, unique=True)

    @property
    def backups_root(self) -> Path:
        return settings.BACKUPS_ROOT / self.key

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


class TwitterSource(models.Model):
    consumer_key = models.CharField(max_length=50, blank=False)
    consumer_secret = models.CharField(max_length=50, blank=False)
    access_token = models.CharField(max_length=50, blank=False)
    access_token_secret = models.CharField(max_length=50, blank=False)
    twitter_username = models.CharField(max_length=50, blank=False)

    def __str__(self):
        return f"@{self.twitter_username}"


class RedditSource(models.Model):
    client_id = models.CharField(max_length=50, blank=False)
    client_secret = models.CharField(max_length=50, blank=False)
    user_agent = models.CharField(max_length=100, blank=True)
    reddit_username = models.CharField(max_length=20, blank=False)

    def __str__(self):
        return f"/u/{self.reddit_username}"


class HackerNewsSource(models.Model):
    hackernews_username = models.CharField(max_length=20, blank=False)

    def __str__(self):
        return self.hackernews_username


class RssSource(models.Model):
    feed_url = models.URLField(blank=False)

    def __str__(self):
        return self.feed_url
