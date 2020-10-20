from functools import partial
from models import BackupSource
from apscheduler.schedulers.background import BackgroundScheduler

def backup_source(source):
    pass

def schedule_backups():
    scheduler = BackgroundScheduler()
    sources = BackupSource.objects.all()
    for source in sources:
        scheduler.add_job(partial(backup_source, source), 'cron', hours='*/6')
    scheduler.start()