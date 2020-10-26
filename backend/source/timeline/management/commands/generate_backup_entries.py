from timeline.models import Entry
from backup.models import BackupSource
from datetime import datetime
from django.core.management.base import BaseCommand
from pathlib import Path
import logging
import mimetypes
import os
import pytz
import subprocess
import time

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Deletes and recreates timeline entries for a given source.'

    def is_file_allowed(self, file_path: Path):
        mimetype = mimetypes.guess_type(file_path, strict=False)
        return (
            mimetype.startswith('image/')
            or mimetype.startswith('video/')
            or mimetype.startswith('audio/')
        )

    def get_changed_files(self, source: BackupSource) -> list[Path]:
        for backup in source.backups:
            for changed_file in backup.changed_files():
                if self.is_file_allowed(changed_file):
                    yield changed_file

    def get_file_date(self, file_path: Path) -> datetime:
        return datetime.fromtimestamp(file_path.stat().st_mtime, pytz.UTC)

    def get_schema(self, file_path: Path) -> str:
        schema = 'file'
        guessed_type = mimetypes.guess_type(file_path, strict=False)[0]
        if not guessed_type:
            return schema

        if guessed_type.startswith('image/'):
            schema += '.image'
        
        if guessed_type.startswith('video/'):
            schema += '.video'
        
        elif guessed_type.startswith('audio/'):
            schema += '.audio'
        
        elif guessed_type.startswith('text/'):
            schema += '.text'

        return schema

    def handle(self, *args, **options):
        sources = BackupSource.objects.all()
        logger.info(f"Generating entries for {len(sources)} backup sources")
        for source in sources:
            backups = source.backups
            logger.info(f"Deleting existing entries for {source}")
            Entry.objects.filter(extra_attributes__source=source.id).delete()
            logger.info(f"Generating entries for {source}")
            for backup in backups:
                Entry.objects.bulk_create([
                    Entry(
                        schema=self.get_schema(changed_file),
                        title=changed_file.name,
                        description='',
                        date_on_timeline=self.get_file_date(changed_file),
                        extra_attributes={
                            'path': str(changed_file.resolve()),
                            'source': source.id,
                        }
                    )
                    for changed_file in backup.changed_files()
                ])
        logger.info(f"Backup entries generated.")