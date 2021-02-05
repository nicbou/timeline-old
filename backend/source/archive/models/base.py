import logging
import shutil
from pathlib import Path
from typing import Tuple

from django.db import models

from backend.settings import ARCHIVES_ROOT
from backup.models.base import BaseSource


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
        return ARCHIVES_ROOT / self.key

    @property
    def files_path(self) -> Path:
        """
        Extracted files are put here for further processing. These files will be deleted after processing.
        """
        return self.root_path / 'files'

    @property
    def source_id(self) -> str:
        return self.key

    @property
    def entry_source(self):
        return f"archive/{super().entry_source}"

    def process(self) -> Tuple[int, int]:
        raise NotImplementedError

    def extract_files(self):
        """
        Extracts compressed files from the archive for further processing
        """
        self.files_path.mkdir(parents=True, exist_ok=True)
        logger.info(f'Extracting archive "{self.key}"')
        shutil.unpack_archive(self.archive_file.path, self.files_path)

    def delete_extracted_files(self):
        """
        Deletes files extracted from the archive
        """
        if self.files_path.exists():
            shutil.rmtree(self.files_path)