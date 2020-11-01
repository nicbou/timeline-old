from typing import List

from timeline.file_utils import get_mimetype
from timeline.models import Entry
from backup.models import BackupSource
from datetime import datetime
from django.core.management.base import BaseCommand
from pathlib import Path
import logging
import mimetypes
import pytz

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Deletes and recreates timeline entries for a given source.'

    @staticmethod
    def is_file_allowed(file_path: Path):
        mimetype = get_mimetype(file_path)
        return (
            mimetype and (
                mimetype.startswith('image/')
                or mimetype.startswith('video/')
                or mimetype.startswith('audio/')
            )
        )

    def get_changed_files(self, source: BackupSource) -> List[Path]:
        for backup in source.backups:
            for changed_file in backup.changed_files():
                if self.is_file_allowed(changed_file):
                    yield changed_file

    @staticmethod
    def get_file_date(file_path: Path) -> datetime:
        return datetime.fromtimestamp(file_path.stat().st_mtime, pytz.UTC)

    @staticmethod
    def get_schema(file_path: Path) -> str:
        schema = 'file'
        guessed_type = mimetypes.guess_type(file_path, strict=False)[0]
        if not guessed_type:
            return schema

        if guessed_type.startswith('image/'):
            schema += '.image'
        elif guessed_type.startswith('video/'):
            schema += '.video'
        elif guessed_type.startswith('audio/'):
            schema += '.audio'
        elif guessed_type.startswith('text/'):
            schema += '.text'
        elif guessed_type == 'application/pdf':
            schema += '.document.pdf'

        return schema

    def handle(self, *args, **options):
        process_latest = False  # TODO: Attach to command line parametre
        process_all = False

        sources = BackupSource.objects.all()
        logger.info(f"Generating entries for {len(sources)} backup sources")
        for source in sources:
            latest_entry = Entry.objects\
                .filter(extra_attributes__source=source.key, extra_attributes__backup_date__isnull=False)\
                .order_by('-extra_attributes__backup_date')\
                .first()

            latest_entry_date = (
                datetime.strptime(latest_entry.extra_attributes.get('backup_date'), '%Y-%m-%dT%H:%M:%SZ')
                if latest_entry and 'backup_date' in latest_entry.extra_attributes
                else None
            )

            source_backups = list(source.backups)
            backups_to_process = source_backups
            if latest_entry_date and not process_all:
                if process_latest:
                    backups_to_process = [backup for backup in backups_to_process if backup.date >= latest_entry_date]
                    logger.info(f'Processing all "{source.key}" backups starting from {latest_entry_date}')
                else:
                    backups_to_process = [backup for backup in backups_to_process if backup.date > latest_entry_date]
                    logger.info(f'Processing all "{source.key}" backups after {latest_entry_date}')
            else:
                logger.info(f'Processing all "{source.key}" backups')

            for backup in backups_to_process:
                Entry.objects.filter(
                    extra_attributes__source=source.key,
                    extra_attributes__backup_date=backup.date.strftime('%Y-%m-%dT%H:%M:%SZ')
                ).delete()
                Entry.objects.bulk_create([
                    Entry(
                        schema=self.get_schema(changed_file),
                        title=changed_file.name,
                        description='',
                        date_on_timeline=self.get_file_date(changed_file),
                        extra_attributes={
                            'path': str(changed_file.resolve()),
                            'source': source.key,
                            'backup_date': backup.date.strftime('%Y-%m-%dT%H:%M:%SZ'),
                        }
                    )
                    for changed_file in backup.changed_files()
                ])
            logger.info(f"\"{source.key}\" backup entries generated. {len(backups_to_process)} backups processed, {len(source_backups) - len(backups_to_process)} skipped.")
