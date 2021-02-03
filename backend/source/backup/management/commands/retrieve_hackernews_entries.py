from backup.models.hackernews import HackerNewsSource
from backup.management.commands import BaseSourceProcessingCommand


class Command(BaseSourceProcessingCommand):
    source_class = HackerNewsSource
