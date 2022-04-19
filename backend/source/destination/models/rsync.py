import logging
import subprocess

from django.conf import settings

from source.models.rsync import RsyncConnectionMixin, pathlib_to_rsync_path, str_to_rsync_path, remote_rsync_path
from source.utils.preprocessing import dump_entries
from destination.models.destination import BaseDestination


logger = logging.getLogger(__name__)


class RsyncDestination(RsyncConnectionMixin, BaseDestination):
    """
    Backs up the timeline using rsync
    """
    def get_preprocessing_tasks(self):
        return [
            dump_entries,
        ]

    def process(self, force=False):
        source_dir = pathlib_to_rsync_path(settings.DATA_ROOT)
        destination_dir = str_to_rsync_path(self.path)
        remote_destination = remote_rsync_path(self.user, self.host, destination_dir)
        logger.info(f"Exporting data with rsync to {remote_destination}")
        rsync_command = [
            "rsync",
            "-az",
            "-H",  # Preserve hard links. Avoids retransfering hard linked files in incremental backups
            "--delete",
            "-e", f"ssh -p{self.port}",
            "--timeout", "120",
            source_dir,
            remote_destination,
        ]
        subprocess.check_call(rsync_command)
