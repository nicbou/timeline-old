import logging
from datetime import datetime
from pathlib import Path
from typing import Tuple

from django.db import models, transaction

from backend.settings import MOUNTS_ROOT
from backup.models.source import BaseSource
from backup.utils.files import create_entries_from_files
from timeline.utils.postprocessing import generate_previews

logger = logging.getLogger(__name__)


class FileSystemSource(BaseSource):
    path = models.FilePathField(blank=False, path=str(MOUNTS_ROOT.resolve()), allow_folders=True, allow_files=False)

    source_name = 'filesystem'

    def process(self, force=False) -> Tuple[int, int]:
        return self.create_file_entries(), 0

    @transaction.atomic
    def create_file_entries(self) -> int:
        logger.info(f"Creating entries for {self.entry_source}")
        return len(create_entries_from_files(Path(self.path), source=self, backup_date=datetime.now()))

    def get_postprocessing_tasks(self):
        return [
            generate_previews,
        ]