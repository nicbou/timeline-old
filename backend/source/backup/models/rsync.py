import logging
import subprocess
from datetime import datetime
from fnmatch import fnmatch
from pathlib import Path
from typing import Generator, Tuple

import pytz
from django.conf import settings
from django.db import models, transaction

from backup.utils.files import get_mimetype, get_media_metadata, get_metadata_from_exif
from timeline.models import Entry


logger = logging.getLogger(__name__)


class Backup:
    """Describes set of files created after a single backup run"""

    source = None
    date = None
    date_format = '%Y-%m-%dT%H.%M.%SZ'  # Using colons would break things
    latest_backup_dirname = 'latest'

    def __init__(self, source: 'RsyncSource', date: datetime = None, path: Path = None):
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


class RsyncSource(models.Model):
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

    def process(self) -> Tuple[int, int]:
        self.run_rsync_backup()
        return self.create_file_entries()

    def run_rsync_backup(self):
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
        logger.info(f"Backing up {str(self)} to {str(current_backup.files_path)}")
        log_file = current_backup.log_path.open('w+')
        rsync_command = [
            "rsync",
            "-az",
            "--itemize-changes",
            "--delete",
            "-e", f"ssh -p {self.port}",
            "--filter", ":- .rsyncignore",
            "--link-dest", str(latest_backup.files_path.resolve()),
            source_path,
            dest_path,
        ]
        exit_code = subprocess.call(rsync_command, stdout=log_file, stderr=log_file)

        if exit_code == 0:
            logger.info(f"{self.key} backup successful. Rsync log is at {str(current_backup.log_path)}")
            latest_backup.root_path.unlink(missing_ok=True)
            latest_backup.root_path.symlink_to(current_backup.root_path, target_is_directory=True)
        else:
            """
            In case of failure, the failed backup's directory is not deleted, but /latest will always point to the
            latest successful backup.
            """
            logger.error(f"{str(self)} backup failed (exit code {exit_code}). "
                         f"Rsync log is at {str(current_backup.log_path)}")
            raise Exception("Rsync backup failed")

    def create_file_entries(self):
        """
        Generates entry from the files in the rsync backup
        """
        logger.info(f"Creating entries for {str(self)}")

        backups_to_process = self.get_backups_to_process()
        entries_created = 0
        for backup in backups_to_process:
            with transaction.atomic():
                entries_deleted = Entry.objects.filter(
                    extra_attributes__source=self.key,
                    extra_attributes__backup_date=backup.date.strftime('%Y-%m-%dT%H:%M:%SZ')
                ).delete()[0]

                entries_to_create = []
                for file_in_backup in self.get_files_in_backup(backup):
                    mimetype = get_mimetype(file_in_backup)
                    schema = self.get_schema_from_mimetype(mimetype)
                    entry = Entry(
                        schema=schema,
                        title=file_in_backup.name,
                        description='',
                        date_on_timeline=self.get_file_date(file_in_backup),
                        extra_attributes={
                            'path': str(file_in_backup.resolve()),
                            'source': self.key,
                            'backup_date': backup.date.strftime('%Y-%m-%dT%H:%M:%SZ'),
                        }
                    )

                    if mimetype:
                        entry.extra_attributes['mimetype'] = mimetype

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

                entries_created += len(Entry.objects.bulk_create(entries_to_create))

        logger.info(f"\"{self.key}\" entries generated. "
                    f"{len(backups_to_process)} backups processed, "
                    f"{len(list(self.backups)) - len(backups_to_process)} skipped. "
                    f"There were {entries_deleted} file entries before the backup. There are now {entries_created}.")

        return entries_created, 0

    def get_backups_to_process(self, process_all=False):
        latest_file_entry = Entry.objects\
            .filter(extra_attributes__source=self.key, extra_attributes__backup_date__isnull=False)\
            .order_by('-extra_attributes__backup_date')\
            .first()

        latest_backup_date = (  # The latest backup that generated an entry.
            datetime.strptime(latest_file_entry.extra_attributes.get('backup_date'), '%Y-%m-%dT%H:%M:%SZ')
            if latest_file_entry and 'backup_date' in latest_file_entry.extra_attributes
            else None
        )

        all_backups = list(self.backups)
        new_backups = [backup for backup in all_backups if (not latest_backup_date) or backup.date > latest_backup_date]

        if process_all:
            logger.info(f'Processing all "{self.key}" backups - {len(all_backups)} found')
            backups_to_process = all_backups
        elif any(list(self.get_new_timeline_include_files_in_backup(backup)) for backup in new_backups):
            logger.info(f'Processing all "{self.key}" backups ({settings.TIMELINE_INCLUDE_FILE} files have changed)'
                        f' - {len(all_backups)} found')
            backups_to_process = all_backups
        else:
            backups_to_process = new_backups
            logger.info(f'Processing all "{self.key}" backups after {latest_backup_date} - {len(new_backups)} found')
        return backups_to_process

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
    def get_files_in_backup(backup: Backup) -> Generator[Path, None, None]:
        """
        Only return files that are allowed by the .timelineinclude files in the latest backup.
        """
        latest_backup = backup.source.latest_backup
        timelineinclude_paths = list(latest_backup.files_path.glob(f'**/{settings.TIMELINE_INCLUDE_FILE}'))
        include_paths = []
        for timelineinclude_path in timelineinclude_paths:
            with open(timelineinclude_path, 'r') as timelineinclude_file:
                for line in timelineinclude_file.readlines():
                    glob_path = timelineinclude_path.parent / Path(line.strip())
                    relative_glob_path = glob_path.relative_to(latest_backup.files_path)
                    include_paths.append(backup.files_path / relative_glob_path)

        if len(include_paths) == 0:
            logger.warning(f'No {settings.TIMELINE_INCLUDE_FILE} rules found in {str(latest_backup.files_path)}')
            return (Path(p) for p in [])

        return (
            changed_file for changed_file in backup.changed_files()
            if any(
                # Path.match() doesn't match ** to multiple subdirs, so we use fnmatch
                fnmatch(str(changed_file), str(include_path)) for include_path in include_paths
            )
        )

    @staticmethod
    def get_new_timeline_include_files_in_backup(backup: Backup) -> Generator[Path, None, None]:
        return (file for file in backup.changed_files() if file.name == settings.TIMELINE_INCLUDE_FILE)

    @staticmethod
    def set_plaintext_description(entry: Entry):
        """
        Sets the description attribute for plain text files
        """
        if len(entry.description):
            return
        original_path = Path(entry.extra_attributes['path'])
        with original_path.open('r') as text_file:
            entry.description = text_file.read(settings.MAX_PLAINTEXT_PREVIEW_SIZE)

    @staticmethod
    def set_media_metadata(entry: Entry):
        """
        Sets width, height, duration and codec attributes for media files
        """
        if 'width' in entry.extra_attributes:
            return

        original_path = Path(entry.extra_attributes['path'])
        try:
            original_media_attrs = get_media_metadata(original_path)
            entry.extra_attributes.update(original_media_attrs)
            if entry.extra_attributes.get('mimetype', '').startswith('image') and 'codec' in entry.extra_attributes:
                # JPEG images are treated as MJPEG videos and have a duration of 1 frame
                entry.extra_attributes.pop('duration', None)
                entry.extra_attributes.pop('codec', None)
        except:
            logger.exception(f"Could not read metadata from file #{entry.pk} at {original_path}")
            raise

    @staticmethod
    def set_exif_metadata(entry: Entry):
        if 'camera' in entry.extra_attributes and 'location' in entry.extra_attributes:
            # TODO: Photos with missing exif data will be reprocessed
            return

        original_path = Path(entry.extra_attributes['path'])
        try:
            metadata = get_metadata_from_exif(original_path)
            entry.extra_attributes.update(metadata)
        except:
            logger.exception(f"Could not read exif from file #{entry.pk} at {original_path}")
            raise

    def __str__(self):
        return f"{self.key} ({self.user}@{self.host}:{self.port}, {self.path})"
