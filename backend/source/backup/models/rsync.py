import logging
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from pprint import pprint
from typing import Generator, Tuple, Optional

import pytz
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models, transaction

from backup.models.base import BaseSource
from backup.utils.files import get_files_in_dir, get_include_rules_for_dir, get_files_matching_rules, \
    create_entries_from_files

logger = logging.getLogger(__name__)


class Backup:
    """Describes a single Rsync backup (in a set of iterative backups)"""
    # TODO: Rename to RsyncBackup

    source = None
    date = None
    date_format = '%Y-%m-%dT%H.%M.%SZ'  # Using colons would break things
    latest_backup_dirname = 'latest'

    def __init__(self, source: 'RsyncSource', date: datetime = None, path: Path = None):
        self.source = source
        if date:
            self.date = date.replace(microsecond=0, tzinfo=None)
        elif path:
            if path.name != self.latest_backup_dirname:
                try:
                    self.date = datetime.strptime(path.name, "%Y-%m-%dT%H.%M.%SZ")
                except ValueError:
                    raise ValueError("Invalid path specified. Not a backup directory.")

            assert path.exists(), "Invalid path specified. Path does not exist."

    @property
    def root_path(self) -> Path:
        """
        Where all files for this backup are saved
        """
        if self.date:
            return self.source.backups_root / self.date.strftime(self.date_format)
        else:
            return self.source.backups_root / self.latest_backup_dirname

    @property
    def rsync_log_path(self) -> Path:
        """
        Where the rsync log for this backup is saved
        """
        return self.root_path / 'rsync.log'

    @property
    def files_path(self) -> Path:
        """
        Where the files for this backup are stored
        """
        return self.root_path / 'files'

    def get_changed_files(self) -> Generator[Tuple[Path, str], None, None]:
        """
        List all files that are new, deleted or modified by this backup. The paths are absolute.
        """
        for line in self.rsync_log_path.open('r').readlines():
            if not line[1] == 'f':
                continue  # Not a file

            action = None
            if line[0] == '*' and str(line).startswith('*deleting'):
                action = 'del'
            elif line[0] == '>' and str(line).startswith('>f+++++++++'):
                action = 'new'
            elif line[0] == '>' and not (line[3] == line[4] == '.'):
                action = 'chg'
            else:
                continue

            yield self.files_path / line.split(' ', 1)[1].strip(), action

    def get_files(self) -> Generator[Path, None, None]:
        return get_files_in_dir(self.files_path)

    def get_entries(self):
        return self.source.get_entries().filter(extra_attributes__backup_date=self.date.strftime('%Y-%m-%dT%H:%M:%SZ'))

    @transaction.atomic
    def delete(self):
        """Deletes a backup's entries and files"""
        self.get_entries().delete()
        shutil.rmtree(self.root_path)

    def __eq__(self, other: 'Backup'):
        return self.root_path == other.root_path

    def __str__(self):
        return f"{self.source.key} ({self.date or 'latest'})"


class RsyncSource(BaseSource):
    user = models.CharField(max_length=80, blank=False)
    host = models.CharField(max_length=255, blank=False)
    port = models.PositiveIntegerField(default=22, validators=[MaxValueValidator(65535)])
    path = models.TextField(blank=False)
    key = models.CharField(max_length=80, blank=False, unique=True)
    max_backups = models.PositiveSmallIntegerField(null=True, validators=[MinValueValidator(1)])

    source_name = 'rsync'

    @property
    def backups_root(self) -> Path:
        return settings.BACKUPS_ROOT / self.key

    @property
    def backups(self) -> Generator[Backup, None, None]:
        """
        Returns a list of all rsync backups, from oldest to newest. The '/latest' backup is not returned, because it's
        just a symlink.
        """
        try:
            backup_dirs = sorted(self.backups_root.iterdir())
        except FileNotFoundError:
            return

        for backup_dir in backup_dirs:
            if not backup_dir.is_dir() or backup_dir.name == Backup.latest_backup_dirname:
                continue

            try:
                yield Backup(source=self, path=backup_dir)
            except ValueError:
                continue

    @property
    def oldest_backup(self) -> Backup:
        return next(self.backups)

    @property
    def latest_backup(self) -> Backup:
        return Backup(source=self, date=None)

    def process(self) -> Tuple[int, int]:
        latest_backup = self.run_rsync_backup()
        if latest_backup is None:
            return 0, 0

        self.purge_old_backups()

        return self.create_file_entries(latest_backup), 0

    def run_rsync_backup(self) -> Optional[Backup]:
        """
        Creates an incremental rsync backup
        """
        source_dir = self.path.strip().rstrip('/') + '/'
        source_path = f'{self.user}@{self.host}:"{source_dir}"'

        current_backup = Backup(self, datetime.now(pytz.UTC))
        latest_backup = self.latest_backup

        # Rsync won't sync dotfiles in the root directory, unless you add a trailing slash
        #   https://stackoverflow.com/q/9046749/1067337
        # Pathlib automatically removes trailing slashes:
        #   https://stackoverflow.com/a/47572467/1067337
        current_backup_path = str(current_backup.files_path.resolve() / '_')[:-1]
        latest_backup_path = str(latest_backup.files_path.resolve() / '_')[:-1]

        latest_backup.files_path.mkdir(parents=True, exist_ok=True)

        # Run rsync
        logger.info(f"Backing up {self.entry_source} to {latest_backup_path}")
        rsync_command = [
            "rsync",
            "-az",
            "--itemize-changes",
            "--delete",
            "-e", f"ssh -p {self.port}",
            "--timeout", "120",
            "--filter", ":- .rsyncignore",
            source_path,
            latest_backup_path,
        ]

        log_file = latest_backup.rsync_log_path.open('w+')
        exit_code = subprocess.call(rsync_command, stdout=log_file, stderr=log_file)

        if exit_code != 0:
            """
            In case of failure, delete the backup. Only leave successful backups on the filesystem.
            /latest still points to the latest successful backup.
            """
            logger.error(f"{self.entry_source} backup failed (exit code {exit_code})")

            logger.info(f"Deleting backup files at {str(current_backup.root_path)}")
            current_backup.delete()

            raise Exception("Rsync backup failed")

        has_changed_files = next(latest_backup.get_changed_files(), None) is not None
        if has_changed_files:
            logger.info(f"{self.entry_source} backup successful. Rsync log is at {str(latest_backup.rsync_log_path)}")
            logger.info(f"Creating snapshot of {str(latest_backup.root_path)} at {str(current_backup.root_path)}")

            # We don't use --link-dest, because when we do, deleted files are not logged.
            # https://rsync.samba.narkive.com/9lakR0U3/
            # We get the same result with cp -al:
            # 1. Rsync remote files to /latest. This is our latest backup.
            # 2. Use `cp -al` to create a snapshot of /latest under `current_backup_path`. This creates hard links
            #    instead of copying the files. This is a snapshot of our latest backup on a specific date.
            # 3. When another backup overwrites /latest, the snapshot does not change, and the files are still there.
            current_backup.root_path.mkdir(parents=True, exist_ok=True)
            subprocess.check_call([
                'cp',
                '-al',
                str(latest_backup.root_path) + '/.',
                str(current_backup.root_path) + '/',
            ])
            return current_backup
        else:
            logger.info(f"{self.entry_source} backup successful. No new files.")
            return None

    def purge_old_backups(self) -> int:
        all_backups = list(self.backups)
        if self.max_backups and len(all_backups) > self.max_backups:
            logger.info(f"Purging {len(all_backups) - self.max_backups} old {self.entry_source} backups.")
            extra_backups = all_backups[:self.max_backups * -1]
            for backup in extra_backups:
                backup.delete()
            return len(extra_backups)
        return 0

    @transaction.atomic
    def create_file_entries(self, backup: Backup) -> int:
        """
        Delete all entries for this source, and recreate them from the latest backup. We could update the entries for
        the files that changed only (with get_changed_files), but it's safer to just reprocess everything.
        """
        logger.info(f"Creating entries for {str(backup)}")
        self.get_entries().delete()
        timelineinclude_rules = list(get_include_rules_for_dir(backup.files_path, settings.TIMELINE_INCLUDE_FILE))
        files_on_timeline = list(get_files_matching_rules(backup.get_files(), timelineinclude_rules))
        return len(create_entries_from_files(files_on_timeline, source=self, backup_date=backup.date))

    def __str__(self):
        return f"{self.source_name}/{self.key} ({self.user}@{self.host}:{self.port}, {self.path})"
