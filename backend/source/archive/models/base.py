import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Tuple, Generator, List

import pytz
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models, transaction

from backend.settings import ARCHIVES_ROOT
from source.models.source import BaseSource
from timeline.models import Entry

logger = logging.getLogger(__name__)


def archive_path(instance: 'ArchiveFile', filename: str):
    return instance.archive.root_path / f"archive{Path(filename).suffix}"


class BaseArchive(BaseSource):
    """
    An archive is a Source that is processed only once, because the underlying data does not change.
    """
    description = models.TextField()
    date_processed = models.DateTimeField(null=True)

    class Meta:
        abstract = True

    def extract_entries(self) -> Generator[Entry, None, None]:
        raise NotImplementedError

    def process(self, force=False) -> Tuple[int, int]:
        if self.date_processed and not force:
            logger.debug(f"{self.entry_source} was already processed. Skipping.")
            return 0, 0

        with transaction.atomic():
            self.delete_entries()
            entries_to_create = filter(self.is_entry_in_date_range, self.extract_entries())
            entries_created = Entry.objects.bulk_create(entries_to_create)
            self.date_processed = datetime.now(pytz.UTC)
            self.save()
        return len(entries_created), 0


class ArchiveFile(models.Model):
    archive_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    archive = GenericForeignKey(
        'archive_type',
        'archive_key',
        for_concrete_model=True,
    )
    archive_key = models.CharField(max_length=50, blank=False)
    archive_file = models.FileField(upload_to=archive_path)

    def __str__(self):
        return self.archive_file.path


class FileArchive(BaseArchive):
    """
    A FileArchive is an archive that extracts entries from one or more files.
    """
    archive_files = GenericRelation(ArchiveFile, content_type_field='archive_type', object_id_field='archive_key')
    keep_extracted_files = False

    class Meta:
        abstract = True

    @property
    def root_path(self) -> Path:
        """
        The root under which all files for this archive are stored. It's deleted when the Archive is deleted.
        """
        return ARCHIVES_ROOT / self.source_name / self.key

    def get_archive_files(self) -> List[Path]:
        return [Path(archive_file.archive_file.path).resolve() for archive_file in self.archive_files.all()]

    def process(self, force=False) -> Tuple[int, int]:
        if self.date_processed and not force:
            logger.debug(f"{self.entry_source} was already processed. Skipping.")
            return 0, 0

        try:
            created_entries, updated_entries = super().process(force=force)
        except KeyboardInterrupt:
            raise
        except:
            logger.exception(f'Failed to process archive "{self.entry_source}"')
            raise
        return created_entries, updated_entries

    def post_delete(self):
        super().post_delete()
        shutil.rmtree(self.root_path, ignore_errors=True)


class CompressedFileArchive(FileArchive):
    """
    A CompressedFileArchive is an archive that extracts entries from one or more compressed files.
    """
    # Some archives contain photos and other attachments. These can be kept after processing the archive, so that the
    # frontend can serve them.
    keep_extracted_files = False

    class Meta:
        abstract = True

    def process(self, force=False) -> Tuple[int, int]:
        if self.date_processed and not force:
            logger.debug(f"{self.entry_source} was already processed. Skipping.")
            return 0, 0

        try:
            self.delete_extracted_files()
            self.extract_compressed_files()
            created_entries, updated_entries = super().process(force=force)
        except KeyboardInterrupt:
            raise
        except:
            logger.exception(f'Failed to process compressed archive "{self.entry_source}"')
            raise
        finally:
            if not self.keep_extracted_files:
                self.delete_extracted_files()
        return created_entries, updated_entries

    @property
    def extracted_files_path(self) -> Path:
        return self.root_path / 'files'

    def extract_compressed_files(self):
        self.extracted_files_path.mkdir(parents=True)
        archive_files = self.get_archive_files()
        logger.info(f'Extracting archive "{self.entry_source}" - {len(archive_files)} files to extract')
        for archive_file in archive_files:
            shutil.unpack_archive(archive_file, self.extracted_files_path)

    def delete_extracted_files(self):
        logger.info(f'Deleting extracted files for "{self.entry_source}"')
        if self.extracted_files_path.exists():
            shutil.rmtree(self.extracted_files_path, ignore_errors=True)
