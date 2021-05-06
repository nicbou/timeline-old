import logging

from backup.management.commands import ModelProcessingCommand
from backup.models.source import BaseSource

logger = logging.getLogger(__name__)


class Command(ModelProcessingCommand):
    class_name = 'source/archive'
    default_class = BaseSource

    def process_instance(self, instance, force):
        created_entries, updated_entries = super().process_instance(instance, force)
        logger.info(
            f"Retrieved {created_entries + updated_entries} entries for {instance}. "
            f"{created_entries} created, {updated_entries} updated."
        )
        return created_entries, updated_entries