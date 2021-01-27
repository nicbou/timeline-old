from backup.management.commands.retrieve_source_entries import BaseSourceProcessingCommand
from backup.models.rsync import RsyncSource


class Command(BaseSourceProcessingCommand):
    source_class = RsyncSource
