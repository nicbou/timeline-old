import logging

from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)


class BaseSourceProcessingCommand(BaseCommand):
    source_class = None

    def handle(self, *args, **options):
        sources = self.source_class.objects.all()
        source_count = len(sources)
        failure_count = 0

        logger.info(f"Backing up {source_count} {self.source_class.__name__} sources")
        for source in sources:
            try:
                created_entries, updated_entries = source.process()
                logger.info(
                    f"Retrieved {created_entries + updated_entries} entries for {source}. "
                    f"{created_entries} created, {updated_entries} updated."
                )
            except:
                logger.exception(f"Failed to back up {str(source)} entries")
                failure_count += 1

        logger.info(f"All {self.source_class.__name__} backups finished. "
                    f"{source_count - failure_count} successful, {failure_count} failed.")
