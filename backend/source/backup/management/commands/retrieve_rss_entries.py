from backup.management.commands.retrieve_source_entries import BaseSourceProcessingCommand
from backup.models.rss import RssSource


class Command(BaseSourceProcessingCommand):
    source_class = RssSource
