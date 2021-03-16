import logging
import shutil
import subprocess
from datetime import datetime
from fnmatch import fnmatch
from pathlib import Path
from typing import Generator, Tuple, Optional

import pytz
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models, transaction

from backup.models.base import BaseSource
from backup.utils.files import get_mimetype, get_media_metadata, get_metadata_from_exif, get_checksum
from timeline.models import Entry


logger = logging.getLogger(__name__)


class Backup:
    """Describes and manages the files created by a single backup run"""

    source = None
    date = None
    date_format = '%Y-%m-%dT%H.%M.%SZ'  # Using colons would break things
    latest_backup_dirname = 'latest'

    def __init__(self, source: 'RsyncSource', date: datetime = None, path: Path = None):
        self.source = source
        if date:
            self.date = date.replace(microsecond=0, tzinfo=None)
        elif path:
            try:
                self.date = datetime.strptime(path.name, "%Y-%m-%dT%H.%M.%SZ")
            except ValueError:
                raise ValueError("Invalid path specified. Not a backup directory.")

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

    def get_changed_files(self) -> Generator[Path, None, None]:
        """
        List all files that are new or modified in this backup
        """

        # When processing the oldest backup, assume that all files are new. The rsync log shows files that changed
        # since the previous backup, but that backup might have been deleted.
        if self == self.source.oldest_backup:
            yield from self.get_files()
        else:
            for line in self.rsync_log_path.open('r').readlines():
                is_file = line[1] == 'f'
                has_content_changed = line[0] == '>' and not (line[3] == line[4] == '.')
                if is_file and has_content_changed:
                    yield self.files_path / line.split(' ', 1)[1].strip()

    def get_files(self) -> Generator[Path, None, None]:
        """
        List all files in this backup
        """
        for path in self.files_path.rglob('*'):
            if path.is_file():
                yield path

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
        return f"{self.source.key} ({self.date})"


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
            if not backup_dir.is_dir():
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
        entries_created = 0
        latest_backup = self.run_rsync_backup()
        if latest_backup is None:
            return 0, 0

        timelineinclude_has_changed = list(filter(
            lambda file: file.name == settings.TIMELINE_INCLUDE_FILE,
            latest_backup.get_changed_files()
        ))

        backups_were_purged = self.purge_old_backups() > 0

        if timelineinclude_has_changed:
            # Reprocess all backups, because we changed which files are included on the timeline
            logger.info(f'{settings.TIMELINE_INCLUDE_FILE} files have changed. Reprocessing all backups.')
            entries_created = sum(self.create_file_entries(backup) for backup in self.backups)
        else:
            if backups_were_purged and len(list(self.backups)) > 1:
                # If older backups were deleted, all files created before the current oldest backup will be missing.
                # We must reprocess the oldest backup, and treat all files in it as new.
                # -
                # If the oldest backup and the latest backup are the same, don't process it twice.
                entries_created += self.create_file_entries(self.oldest_backup)

            entries_created += self.create_file_entries(latest_backup)

        return entries_created, 0

    def run_rsync_backup(self) -> Optional[Backup]:
        current_backup = Backup(self, datetime.now(pytz.UTC))
        latest_backup = self.latest_backup

        source_dir = self.path.strip().rstrip('/') + '/'
        source_path = f'{self.user}@{self.host}:"{source_dir}"'

        # Rsync won't sync dotfiles in the root directory, unless you add a trailing slash
        #   https://stackoverflow.com/q/9046749/1067337
        # Pathlib automatically removes trailing slashes:
        #   https://stackoverflow.com/a/47572467/1067337
        dest_path = str(current_backup.files_path.resolve() / '_')[:-1]

        current_backup.files_path.mkdir(parents=True, exist_ok=True)

        # Run rsync
        logger.info(f"Backing up {self.source_name} to {str(current_backup.files_path)}")
        log_file = current_backup.rsync_log_path.open('w+')
        rsync_command = [
            "rsync",
            "-az",
            "--itemize-changes",
            "--delete",
            "-e", f"ssh -p {self.port}",
            "--timeout", "120",
            "--filter", ":- .rsyncignore",
            "--link-dest", str(latest_backup.files_path.resolve()),
            source_path,
            dest_path,
        ]
        exit_code = subprocess.call(rsync_command, stdout=log_file, stderr=log_file)

        if exit_code != 0:
            """
            In case of failure, delete the backup. Only leave successful backups on the filesystem.
            /latest still points to the latest successful backup.
            """
            logger.error(f"{self.source_name} backup failed (exit code {exit_code})")

            logger.info(f"Deleting backup files at {str(current_backup.root_path)}")
            current_backup.delete()

            raise Exception("Rsync backup failed")

        has_changed_files = next(current_backup.get_changed_files(), None) is not None
        if has_changed_files:
            logger.info(f"{self.source_name} backup successful. Rsync log is at {str(current_backup.rsync_log_path)}")

            # Symlink /latest to the new backup
            latest_backup.root_path.unlink(missing_ok=True)
            latest_backup.root_path.symlink_to(current_backup.root_path, target_is_directory=True)
            return current_backup
        else:
            current_backup.delete()
            logger.info(f"{self.source_name} backup successful. No new files.")
            return None

    def purge_old_backups(self) -> int:
        all_backups = list(self.backups)
        if self.max_backups and len(all_backups) > self.max_backups:
            logger.info(f"Purging {len(all_backups) - self.max_backups} old {self.source_name} backups.")
            extra_backups = all_backups[:self.max_backups * -1]
            for backup in extra_backups:
                backup.delete()
            return len(extra_backups)
        return 0

    @transaction.atomic
    def create_file_entries(self, backup: Backup) -> int:
        logger.info(f"Creating entries for {str(backup)}")
        backup.get_entries().delete()

        entries_to_create = []
        for file_in_backup in self.get_timeline_files_in_backup(backup):
            mimetype = get_mimetype(file_in_backup)
            schema = self.get_schema_from_mimetype(mimetype)
            entry = Entry(
                schema=schema,
                source=self.entry_source,
                title=file_in_backup.name,
                description='',
                date_on_timeline=self.get_file_date(file_in_backup),
                extra_attributes={
                    'file': {
                        'path': str(file_in_backup.resolve()),
                        'checksum': get_checksum(file_in_backup),
                    },
                    'backup_date': backup.date.strftime('%Y-%m-%dT%H:%M:%SZ'),
                }
            )

            if mimetype:
                entry.extra_attributes['file']['mimetype'] = mimetype

            if schema == 'file.text' or schema.startswith('file.text'):
                self.set_plaintext_description(entry)

            if (
                schema == 'file.image' or schema.startswith('file.image')
                or schema == 'file.video' or schema.startswith('file.video')
            ):
                self.set_media_metadata(entry)

            if schema == 'file.image' or schema.startswith('file.image'):
                self.set_exif_metadata(entry)

            entries_to_create.append(entry)

        return len(Entry.objects.bulk_create(entries_to_create))

    def get_timeline_files_in_backup(self, backup: Backup) -> Generator[Path, None, None]:
        """
        Only return files that are allowed by the latest backup's .timelineinclude files. The .timelineinclude files in
        older backups are not considered.
        """
        timelineinclude_paths = list(self.latest_backup.files_path.rglob(settings.TIMELINE_INCLUDE_FILE))
        include_paths = []
        for timelineinclude_path in timelineinclude_paths:
            with open(timelineinclude_path, 'r') as timelineinclude_file:
                for line in timelineinclude_file.readlines():
                    glob_path = timelineinclude_path.parent / Path(line.strip())
                    relative_glob_path = glob_path.relative_to(self.latest_backup.files_path)
                    include_paths.append(backup.files_path / relative_glob_path)

        if len(include_paths) == 0:
            logger.warning(f'No {settings.TIMELINE_INCLUDE_FILE} rules found in {str(self.latest_backup.files_path)}')
            return  # Empty generator

        for file in backup.get_changed_files():
            # Path.match() doesn't match ** to multiple subdirs, so we use fnmatch
            if any(fnmatch(str(file), str(include_path)) for include_path in include_paths):
                yield file

    @staticmethod
    def get_file_date(file_path: Path) -> datetime:
        return datetime.fromtimestamp(file_path.stat().st_mtime, pytz.UTC)

    @staticmethod
    def get_schema_from_mimetype(mimetype) -> str:
        schema = 'file'
        if not mimetype:
            return schema

        if mimetype.startswith('image/'):
            schema += '.image'
        elif mimetype.startswith('video/'):
            schema += '.video'
        elif mimetype.startswith('audio/'):
            schema += '.audio'
        elif mimetype.startswith('text/'):
            # TODO: Handle text/markdown
            schema += '.text'
        elif mimetype == 'application/pdf':
            schema += '.document.pdf'

        return schema

    @staticmethod
    def set_plaintext_description(entry: Entry):
        """
        Sets the description attribute for plain text files
        """
        if len(entry.description):
            return
        original_path = Path(entry.extra_attributes['file']['path'])
        with original_path.open('r') as text_file:
            entry.description = text_file.read(settings.MAX_PLAINTEXT_PREVIEW_SIZE)

    @staticmethod
    def set_media_metadata(entry: Entry):
        """
        Sets width, height, duration and codec attributes for media files
        """
        if 'media' in entry.extra_attributes:
            # Information is already set
            return

        entry.extra_attributes['media'] = {}
        original_path = Path(entry.extra_attributes['file']['path'])
        try:
            original_media_attrs = get_media_metadata(original_path)
            entry.extra_attributes['media'].update(original_media_attrs)
            if (
                entry.extra_attributes['file'].get('mimetype').startswith('image')
                and 'codec' in entry.extra_attributes['media']
            ):
                # JPEG images are treated as MJPEG videos and have a duration of 1 frame
                entry.extra_attributes['media'].pop('duration', None)
                entry.extra_attributes['media'].pop('codec', None)
        except:
            logger.exception(f"Could not read metadata from file #{entry.pk} at {original_path}")
            raise

    @staticmethod
    def set_exif_metadata(entry: Entry):
        if 'camera' in entry.extra_attributes.get('media', {}) or 'location' in entry.extra_attributes:
            # TODO: Photos with missing exif data will be reprocessed
            return

        original_path = Path(entry.extra_attributes['file']['path'])
        try:
            metadata = get_metadata_from_exif(original_path)
            if 'media' in metadata:
                entry.extra_attributes['media'].update(metadata['media'])
            if 'location' in metadata:
                entry.extra_attributes['location'] = metadata['location']
        except:
            logger.exception(f"Could not read exif from file #{entry.pk} at {original_path}")
            raise

    def __str__(self):
        return f"{self.source_name}/{self.key} ({self.user}@{self.host}:{self.port}, {self.path})"
