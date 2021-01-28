from backup.models.hackernews import HackerNewsSource
from backup.management.commands.retrieve_source_entries import BaseSourceProcessingCommand


class Command(BaseSourceProcessingCommand):
    source_class = HackerNewsSource
