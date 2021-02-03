from backup.management.commands import BaseSourceProcessingCommand
from backup.models.rsync import RsyncSource


class Command(BaseSourceProcessingCommand):
    source_class = RsyncSource
