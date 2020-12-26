import logging
from typing import List

from django.core.management.base import BaseCommand

from timeline.models import Entry

logger = logging.getLogger(__name__)


class BasePostRetrievalCommand(BaseCommand):
    entry_name_plural = 'posts'
    source_class = None

    def update_entries_from_source(self, source: source_class) -> List[Entry]:
        raise NotImplementedError

    def handle(self, *args, **options):
        sources = self.source_class.objects.all()
        source_count = len(sources)
        failure_count = 0

        logger.info(f"Backing up {self.entry_name_plural} from {source_count} sources")
        for source in sources:
            try:
                created_entries, updated_entries = self.update_entries_from_source(source)
                logger.info(
                    f"Retrieved {len(created_entries) + len(updated_entries)} {self.entry_name_plural} for {source}. "
                    f"{len(created_entries)} created, {len(updated_entries)} updated."
                )
            except:
                logger.exception(f"Failed to back up {source} {self.entry_name_plural}")
                failure_count += 1

        logger.info(f"All {self.entry_name_plural} backups finished. "
                    f"{source_count - failure_count} successful, {failure_count} failed.")
