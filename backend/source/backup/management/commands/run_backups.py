from backup.models import BackupSource, Backup
from datetime import datetime
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
import logging
import pytz
import subprocess


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Backs up the remote sources one by one.'

    def backup_source(self, source: BackupSource):
        current_backup = Backup(source, datetime.now(pytz.UTC))
        latest_backup = Backup(source)

        source_dir = source.path.strip().rstrip('/') + '/'
        source_path = f'{source.user}@{source.host}:"{source_dir}"'

        current_backup.files_path.mkdir(parents=True, exist_ok=True)

        # Run rsync
        logger.info(f"Backing up {source.key} ({source_path}) to {str(current_backup.files_path)}")
        log_file = current_backup.log_path.open('w+')
        rsync_command = [
            "rsync",
            "-az",
            "--itemize-changes",
            "--delete",
            "-e", f"ssh -p {source.port}",
            "--filter", ":- .rsyncignore",
            "--link-dest", str(latest_backup.files_path.resolve()),
            source_path,
            str(current_backup.files_path.resolve()),
        ]
        exit_code = subprocess.call(rsync_command, stdout=log_file, stderr=log_file)

        if exit_code == 0:
            logger.info(f"{source.key} backup successful. Rsync log is at {str(current_backup.log_path)}")
            latest_backup.root_path.unlink(missing_ok=True)
            latest_backup.root_path.symlink_to(current_backup.root_path, target_is_directory=True)
        else:
            logger.error(f"{source} backup failed (exit code {exit_code}). Rsync log is at {str(current_backup.log_path)}")
            raise Exception("Rsync backup failed")

    def handle(self, *args, **options):
        sources = BackupSource.objects.all()
        logger.info(f"Backing up {len(sources)} sources")
        failure_count = 0
        for source in sources:
            try:
                self.backup_source(source)
            except:
                logger.exception(f"Failed to back up {source}")
                failure_count += 1
        logger.info(f"All backups finished. {len(sources) - failure_count} successful, {failure_count} failed.")