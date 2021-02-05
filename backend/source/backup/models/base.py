import logging
from typing import Tuple

from django.db import models

from timeline.models import Entry


logger = logging.getLogger(__name__)


class BaseSourceManager(models.Manager):
    def process(self):
        sources = self.all()
        source_count = sources.count()
        logger.info(f"Processing {source_count} sources")
        failure_count = 0
        for source in sources:
            try:
                created_entries, updated_entries = source.process()
                logger.info(
                    f"Retrieved {created_entries + updated_entries} entries for {source}. "
                    f"{created_entries} created, {updated_entries} updated."
                )
            except:
                logger.exception(f"Failed to process {str(source)}")
                failure_count += 1
                pass
        logger.info(f"{source_count} sources processed. "
                    f"{source_count - failure_count} successful, {failure_count} failed.")


class BaseSource(models.Model):
    objects = BaseSourceManager()

    class Meta:
        abstract = True

    @property
    def source_name(self) -> str:
        return type(self).__name__

    @property
    def source_id(self) -> str:
        return str(self.pk)

    @property
    def entry_source(self) -> str:
        """
        A "source" value shared by all entries created by this Source instance.

        For example "twitter/katyperry" or "rsync/macbook"
        """
        return f"{self.source_name}/{self.source_id}"

    def __str__(self) -> str:
        return self.entry_source

    def get_entries(self):
        return Entry.objects.filter(source=self.entry_source)

    def delete_entries(self):
        deleted_count = self.get_entries().delete()[0]
        logger.info(f'Deleted {deleted_count} existing entries for archive "{str(self)}"')
        return deleted_count

    def process(self) -> Tuple[int, int]:
        """
        Extract and create entries for this source
        """
        raise NotImplementedError