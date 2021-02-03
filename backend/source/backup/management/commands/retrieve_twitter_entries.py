from backup.management.commands import BaseSourceProcessingCommand
from backup.models.twitter import TwitterSource


class Command(BaseSourceProcessingCommand):
    source_class = TwitterSource
