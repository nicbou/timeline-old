import logging
from datetime import datetime
from functools import partial
from pathlib import Path
from typing import Tuple

from django.db import models, transaction

from backend.settings import MOUNTS_ROOT
from source.models.source import BaseSource
from source.utils.files import create_entries_from_directory
from timeline.utils.postprocessing import generate_previews

logger = logging.getLogger(__name__)


class FileSystemSource(BaseSource):
    path = models.FilePathField(blank=False, path=str(MOUNTS_ROOT.resolve()), allow_folders=True, allow_files=False)

    def process(self, force=False) -> Tuple[int, int]:
        return self.create_file_entries(use_cache=(not force)), 0

    @transaction.atomic
    def create_file_entries(self, use_cache=True) -> int:
        logger.info(f"Creating entries for {self.entry_source}")
        return len(
            create_entries_from_directory(Path(self.path), source=self, backup_date=datetime.now(), use_cache=use_cache)
        )

    def get_postprocessing_tasks(self):
        return super().get_postprocessing_tasks() + [
            partial(generate_previews, source=self),
        ]
