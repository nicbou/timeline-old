from backup.management.commands.retrieve_source_entries import BaseSourceProcessingCommand
from backup.models.reddit import RedditSource


class Command(BaseSourceProcessingCommand):
    source_class = RedditSource
