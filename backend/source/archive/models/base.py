import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Tuple, Generator

import pytz
from django.db import models, transaction

from backend.settings import ARCHIVES_ROOT
from backup.models.source import BaseSource
from timeline.models import Entry

logger = logging.getLogger(__name__)


def archive_path(instance: 'BaseArchive', filename: str):
    return instance.root_path / f"archive{Path(filename).suffix}"


class BaseArchive(BaseSource):
    key = models.SlugField(max_length=80, allow_unicode=True, primary_key=True)
    description = models.TextField()
    date_processed = models.DateTimeField(null=True)
    archive_file = models.FileField(upload_to=archive_path)

    class Meta:
        abstract = True

    @property
    def root_path(self) -> Path:
        """
        The root under which all files for this archive are stored.
        """
        return ARCHIVES_ROOT / self.source_name / self.key

    @property
    def files_path(self) -> Path:
        """
        Extracted files are put here for further processing. These files will be deleted after processing.
        """
        return self.root_path / 'files'

    def extract_entries(self) -> Generator[Entry, None, None]:
        raise NotImplementedError

    def process(self, force=False) -> Tuple[int, int]:
        if self.date_processed and not force:
            logger.info(f"Archive {self.entry_source} was already processed. Skipping.")
            return 0, 0

        with transaction.atomic():
            self.delete_entries()
            entries_to_create = self.extract_entries()
            entries_created = Entry.objects.bulk_create(entries_to_create)
            self.date_processed = datetime.now(pytz.UTC)
            self.save()
        return len(entries_created), 0


class CompressedArchive(BaseArchive):
    class Meta:
        abstract = True

    def process(self, force=False) -> Tuple[int, int]:
        if self.date_processed and not force:
            logger.info(f"Archive {self.entry_source} was already processed. Skipping.")
            return 0, 0

        try:
            self.delete_extracted_files()
            self.extract_compressed_files()
            created_entries, updated_entries = super().process(force=force)
        except:
            logger.exception(f'Failed to process archive "{self.entry_source}"')
            raise
        finally:
            self.delete_extracted_files()
        return created_entries, updated_entries

    def extract_compressed_files(self):
        self.files_path.mkdir(parents=True, exist_ok=True)
        logger.info(f'Extracting archive "{self.entry_source}"')
        shutil.unpack_archive(self.archive_file.path, self.files_path)

    def delete_extracted_files(self):
        logger.info(f'Deleting extracted files for "{self.entry_source}"')
        if self.files_path.exists():
            shutil.rmtree(self.files_path)
