import logging
import shutil
import subprocess
from datetime import datetime
from functools import partial
from pathlib import Path
from typing import Generator, Tuple, Optional

import pytz
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models, transaction

from backup.models.destination import BaseDestination
from backup.models.source import BaseSource
from backup.utils.datetime import datetime_to_json
from backup.utils.files import get_files_in_dir, create_entries_from_files
from backup.utils.preprocessing import dump_entries
from backup.utils.ssh import KEY_EXCHANGE_SSH_COPY_ID, KEY_EXCHANGE_METHODS
from timeline.utils.postprocessing import generate_previews

logger = logging.getLogger(__name__)


def pathlib_to_rsync_path(path: Path) -> str:
    return str_to_rsync_path(str(path.resolve()))

def str_to_rsync_path(path: str) -> str:
    # Rsync won't sync dotfiles in the root directory, unless you add a trailing slash
    #   https://stackoverflow.com/q/9046749/1067337
    # Pathlib automatically removes trailing slashes:
    #   https://stackoverflow.com/a/47572467/1067337
    return path.strip().rstrip('/') + '/'


def remote_rsync_path(user: str, host: str, path: str) -> str:
    return f'{user}@{host}:"{path}"'


class RsyncConnectionMixin(models.Model):
    user = models.CharField(max_length=80, blank=False)
    host = models.CharField(max_length=255, blank=False)
    port = models.PositiveIntegerField(default=22, validators=[MaxValueValidator(65535)])
    path = models.TextField(blank=False)
    key_exchange_method = models.CharField(
        max_length=20,
        choices=[(method, method) for method in KEY_EXCHANGE_METHODS],
        default=KEY_EXCHANGE_SSH_COPY_ID
    )

    class Meta:
        abstract = True

    def __str__(self):
        return f"{super().__str__()} ({self.user}@{self.host}:{self.port}, {self.path})"


class RsyncBackup:
    """Describes a single Rsync backup (in a set of iterative backups)"""

    source = None
    date = None
    date_format = '%Y-%m-%dT%H.%M.%SZ'  # Colons are not always allowed in file names
    latest_backup_dirname = 'latest'

    def __init__(self, source: 'RsyncSource', date: datetime = None, path: Path = None):
        self.source = source
        if date:
            self.date = date.replace(microsecond=0, tzinfo=None)
        elif path:
            if path.name != self.latest_backup_dirname:
                try:
                    self.date = datetime.strptime(path.name, self.date_format)
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
            absolute_path = self.files_path / line.split(' ', 1)[1].strip()

            if line[0] == '*' and line.startswith('*deleting'):
                yield absolute_path, 'del'
            elif line[1] == 'f' and line[0] == '>':
                if str(line).startswith('>f+++++++++'):
                    yield absolute_path, 'new'
                elif line[3] != '.' and line[4] != '.':
                    yield absolute_path, 'chg'

    def get_files(self) -> Generator[Path, None, None]:
        return get_files_in_dir(self.files_path)

    def get_entries(self):
        return self.source.get_entries().filter(extra_attributes__backup_date=datetime_to_json(self.date))

    @transaction.atomic
    def delete(self):
        """Deletes a backup's entries and files"""
        self.get_entries().delete()
        shutil.rmtree(self.root_path)

    def __eq__(self, other: 'RsyncBackup'):
        return self.root_path == other.root_path

    def __str__(self):
        return f"{self.source.key} ({self.date or 'latest'})"


class RsyncSource(RsyncConnectionMixin, BaseSource):
    max_backups = models.PositiveSmallIntegerField(null=True, validators=[MinValueValidator(1)])

    @property
    def backups_root(self) -> Path:
        return settings.BACKUPS_ROOT / self.source_name / self.key

    @property
    def backups(self) -> Generator[RsyncBackup, None, None]:
        """
        Returns a list of all rsync backups, from oldest to newest. The '/latest' backup is not returned, because it's
        just a symlink.
        """
        try:
            backup_dirs = sorted(self.backups_root.iterdir())
        except FileNotFoundError:
            return

        for backup_dir in backup_dirs:
            if not backup_dir.is_dir() or backup_dir.name == RsyncBackup.latest_backup_dirname:
                continue

            try:
                yield RsyncBackup(source=self, path=backup_dir)
            except ValueError:
                continue

    @property
    def oldest_backup(self) -> RsyncBackup:
        return next(self.backups)

    @property
    def latest_backup(self) -> RsyncBackup:
        return RsyncBackup(source=self, date=None)

    def process(self, force=False) -> Tuple[int, int]:
        current_backup = self.run_rsync_backup()
        self.purge_old_backups()
        if current_backup or force:
            return self.create_file_entries(use_cache=(not force)), 0
        else:
            return 0, 0

    def run_rsync_backup(self) -> Optional[RsyncBackup]:
        """
        Creates an incremental rsync backup
        """
        current_backup = RsyncBackup(self, datetime.now(pytz.UTC))
        current_backup_path = pathlib_to_rsync_path(current_backup.files_path)

        # Copy the latest backup's file to the current backup's dir. Rsync will overwrite those files, but only if they
        # are new. We use hard links, so no disk space is used.
        latest_backup = self.latest_backup
        current_backup.files_path.mkdir(parents=True, exist_ok=False)

        if latest_backup.files_path.exists():  # There might not be a /latest backup
            subprocess.check_call([
                'cp',
                '-al',
                str(latest_backup.files_path) + '/.',
                str(current_backup.files_path) + '/',
            ])

        # Run rsync. Only transfer files that are different from what's in the current backup.
        logger.info(f"Backing up {self.entry_source} to {current_backup_path}")
        source_dir = pathlib_to_rsync_path(Path(self.path))
        source_path = remote_rsync_path(self.user, self.host, source_dir)
        rsync_command = [
            "rsync",
            "-az",
            "--itemize-changes",
            "--delete",
            "-e", f"ssh -p {self.port}",
            "--timeout", "120",
            "--filter", ":- .rsyncignore",
            source_path,
            current_backup_path,
        ]

        rsync_log_file = current_backup.rsync_log_path.open('w+')
        rsync_exit_code = subprocess.call(rsync_command, stdout=rsync_log_file, stderr=rsync_log_file)

        if rsync_exit_code != 0:
            # In case of failure, delete the backup. Only leave successful backups on the filesystem. /latest still
            # points to the latest successful backup.
            logger.error(f"{self.entry_source} backup failed (exit code {rsync_exit_code})")
            logger.info(f"Deleting backup files at {str(current_backup.root_path)}")
            current_backup.delete()
            raise Exception("Rsync backup failed")

        changed_files_count = len(list(current_backup.get_changed_files()))
        logger.info(f"{self.entry_source} backup successful. "
                    f"{changed_files_count} files changed. "
                    f"Rsync log is at {str(current_backup.rsync_log_path)}")

        if changed_files_count == 0:
            # Don't keep multiple identical backups. If `max_backups` is set, it pushes older backups out.
            logger.info("Deleting backup because no files have changed.")
            current_backup.delete()
            return None

        # Hard link /latest to the current backup
        # The root_path paths are absolute. We convert them to relative paths, to ensure they keep working if the
        # backups are moved elsewhere.
        latest_backup.root_path.unlink(missing_ok=True)
        latest_backup.root_path.symlink_to(current_backup.root_path.name, target_is_directory=True)

        return current_backup

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
    def create_file_entries(self, use_cache=True) -> int:
        """
        Delete all entries for this source, and recreate them from the latest backup. We could update the entries for
        the files that changed only (with get_changed_files), but it's safer to just reprocess everything.
        """
        try:
            latest_backup = list(self.backups)[-1]  # self.latest_backup does not have a .date
        except IndexError:
            logger.info(f'{str(self)} has no backups to process.')
            return 0

        logger.info(f"Creating entries for {str(latest_backup)}")
        return len(create_entries_from_files(
            latest_backup.files_path,
            source=self,
            backup_date=latest_backup.date,
            use_cache=use_cache
        ))

    def get_postprocessing_tasks(self):
        return [
            partial(generate_previews, source=self),
        ]


class RsyncDestination(RsyncConnectionMixin, BaseDestination):
    """
    Backs up the timeline using rsync
    """
    def get_preprocessing_tasks(self):
        return [
            dump_entries,
        ]

    def process(self, force=False):
        source_dir = pathlib_to_rsync_path(settings.DATA_ROOT)
        destination_dir = str_to_rsync_path(self.path)
        remote_destination = remote_rsync_path(self.user, self.host, destination_dir)
        logger.info(f"Exporting data with rsync to {remote_destination}")
        rsync_command = [
            "rsync",
            "-az",
            "-H",  # Preserve hard links. Avoids retransfering hard linked files in incremental backups
            "--delete",
            "-e", f"ssh -p{self.port}",
            "--timeout", "120",
            source_dir,
            remote_destination,
        ]
        subprocess.check_call(rsync_command)
