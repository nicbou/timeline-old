import logging
from typing import Tuple, Iterable

from django.db import models

from timeline.models import Entry

logger = logging.getLogger(__name__)


class BaseSource(models.Model):
    key = models.SlugField(max_length=80, primary_key=True)

    class Meta:
        abstract = True
        ordering = ['key']

    @property
    def source_name(self) -> str:
        return type(self).__name__

    @property
    def entry_source(self) -> str:
        """
        A "source" value shared by all entries created by this Source instance.
        For example "TwitterSource/katyperry" or "RsyncSource/macbook"
        """
        return f"{self.source_name}/{self.key}"

    def __str__(self) -> str:
        return self.entry_source

    def get_entries(self):
        return Entry.objects.filter(source=self.entry_source)

    def delete_entries(self):
        deleted_count = self.get_entries().delete()[0]
        logger.info(f'Deleted {deleted_count} existing entries for archive "{str(self)}"')
        return deleted_count

    def get_preprocessing_tasks(self) -> Iterable:
        return []

    def process(self, force=False) -> Tuple[int, int]:
        """
        Extract and create entries for this source
        """
        raise NotImplementedError

    def get_postprocessing_tasks(self) -> Iterable:
        return []