import logging
from datetime import datetime
from pathlib import Path
from typing import Tuple

from django.conf import settings
from django.db import models, transaction

from backend.settings import MOUNTS_ROOT
from backup.models.base import BaseSource
from backup.utils.files import get_include_rules_for_dir, get_files_matching_rules, create_entries_from_files, \
    get_files_in_dir

logger = logging.getLogger(__name__)


class FileSystemSource(BaseSource):
    path = models.FilePathField(blank=False, path=str(MOUNTS_ROOT.resolve()), allow_folders=True, allow_files=False)

    source_name = 'filesystem'

    def process(self, force=False) -> Tuple[int, int]:
        return self.create_file_entries(), 0

    @transaction.atomic
    def create_file_entries(self) -> int:
        logger.info(f"Creating entries for {self.entry_source}")
        self.get_entries().delete()
        timelineinclude_rules = list(get_include_rules_for_dir(Path(self.path), settings.TIMELINE_INCLUDE_FILE))
        files_on_timeline = get_files_matching_rules(get_files_in_dir(Path(self.path)), timelineinclude_rules)
        return len(create_entries_from_files(files_on_timeline, source=self, backup_date=datetime.now()))
