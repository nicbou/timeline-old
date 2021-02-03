from backup.management.commands import BaseSourceProcessingCommand
from backup.models.reddit import RedditSource


class Command(BaseSourceProcessingCommand):
    source_class = RedditSource
