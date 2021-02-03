from backup.management.commands import BaseSourceProcessingCommand
from backup.models.rss import RssSource


class Command(BaseSourceProcessingCommand):
    source_class = RssSource
