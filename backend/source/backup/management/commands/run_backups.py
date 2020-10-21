from backup.models import BackupSource
from datetime import datetime
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
import logging
import os
import subprocess


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Backs up the remote sources one by one.'
    rsync_log_path = settings.RSYNC_LOG_PATH

    def backup_source(self, source):
        logging.info(f"Backing up {source}")

        # Log path
        rsync_log_path = os.path.abspath(self.rsync_log_path.strip().rstrip('/'))
        logging.info(f"Rsync log for {source.key} will be at {rsync_log_path}")
        os.makedirs(os.path.dirname(rsync_log_path), exist_ok=True)
        rsync_log_file = open(rsync_log_path, "w")

        # Source path
        source_dir = source.path.strip().rstrip('/') + '/'
        source_path = f'{source.user}@{source.host}:"{source_dir}"'
        logging.info(f"Source for {source.key} is {source_path}")

        # Destination paths
        destination_dir = os.path.abspath(os.path.join(settings.BACKUPS_ROOT, source.key))
        current_date = datetime.utcnow().strftime("%Y-%m-%dT%H%M%SZ")
        latest_backup_path = os.path.join(destination_dir, 'latest')
        current_backup_path = os.path.join(destination_dir, current_date)
        logging.info(f"Destination for {source.key} is {current_backup_path}")
        os.makedirs(current_backup_path, exist_ok=True)

        # Run rsync
        logger.info(f'Backing up {source_path} to {current_backup_path}...')
        rsync_command = [
            "rsync",
            "-avz",
            "--stats",
            "--delete",
            "-e", f"ssh -p {source.port}",
            "--filter", ":- .rsyncignore",
            "--link-dest", latest_backup_path,
            source_path,
            current_backup_path,
        ]
        exit_code = subprocess.call(rsync_command, stdout=rsync_log_file, stderr=rsync_log_file)

        if exit_code == 0:
            logger.info(f"{source} backup successful. The rsync log is at {rsync_log_path}")
            try:
                os.unlink(latest_backup_path)
            except FileNotFoundError:
                pass  # Symlink does not exist on first backup
            os.symlink(current_backup_path, latest_backup_path, target_is_directory=True)
            logger.info(f"{latest_backup_path} now points to latest backup")
        else:
            logger.error(f"{source} backup failed (exit code {exit_code}). The rsync log is at {rsync_log_path}")
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
        logger.info(f"Backup finished. {len(sources) - failure_count} successful, {failure_count} failed.")