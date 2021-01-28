from backup.management.commands.retrieve_source_entries import BaseSourceProcessingCommand
from backup.models.twitter import TwitterSource


class Command(BaseSourceProcessingCommand):
    source_class = TwitterSource
