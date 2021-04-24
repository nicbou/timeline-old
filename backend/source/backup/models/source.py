import logging
from typing import Tuple, Iterable

from django.db import models

from timeline.models import Entry

logger = logging.getLogger(__name__)


class BaseSourceManager(models.Manager):
    def process(self, force=False):
        sources = self.all()
        source_count = sources.count()
        logger.info(f"Processing {source_count} sources")
        failure_count = 0

        preprocessing_tasks = set()
        postprocessing_tasks = set()

        for source in sources:
            preprocessing_tasks.update(source.get_preprocessing_tasks())
            postprocessing_tasks.update(source.get_postprocessing_tasks())

        logger.info(f"Running {len(preprocessing_tasks)} preprocessing tasks")
        for task in preprocessing_tasks:
            task()

        for source in sources:
            try:
                created_entries, updated_entries = source.process(force=force)
                logger.info(
                    f"Retrieved {created_entries + updated_entries} entries for source {source}. "
                    f"{created_entries} created, {updated_entries} updated."
                )
            except:
                logger.exception(f"Failed to process source {str(source)}")
                failure_count += 1

        logger.info(f"{source_count} sources processed. "
                    f"{source_count - failure_count} successful, {failure_count} failed.")

        logger.info(f"Running {len(postprocessing_tasks)} postprocessing tasks")
        for task in postprocessing_tasks:
            task()


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

    def get_preprocessing_tasks(self) -> Iterable:
        return []

    def process(self, force=False) -> Tuple[int, int]:
        """
        Extract and create entries for this source
        """
        raise NotImplementedError

    def get_postprocessing_tasks(self) -> Iterable:
        return []