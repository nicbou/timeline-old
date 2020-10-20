from django.apps import AppConfig
from tasks import schedule_backups


class BackupConfig(AppConfig):
    name = 'backup'

    def ready(self):
        schedule_backups()