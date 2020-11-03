import logging
from datetime import datetime
from typing import List

import tweepy
from django.core.management.base import BaseCommand
from tweepy import Status

from backup.models import TwitterSource
from timeline.models import Entry

logger = logging.getLogger(__name__)


class BasePostRetrievalCommand(BaseCommand):
    entry_schema = 'social.other.post'
    entry_name_plural = 'posts'
    source_class = None

    def get_entries_from_source(self, source, since_id=None) -> List[Entry]:
        raise NotImplementedError

    def get_latest_entry(self, source) -> Entry:
        raise NotImplementedError

    def get_latest_entry_date(self, latest_entry: Entry):
        return latest_entry.date_on_timeline if latest_entry else None

    def get_latest_entry_id(self, latest_entry: Entry):
        return latest_entry.extra_attributes.get('post_id') if latest_entry else None

    def add_arguments(self, parser):
        parser.add_argument(
            '--process-all',
            action='store_true',
            help=f'Reprocess already processed {self.entry_name_plural}',
        )

    def handle(self, *args, **options):
        sources = self.source_class.objects.all()
        source_count = len(sources)
        failure_count = 0

        logger.info(f"Backing up {self.entry_name_plural} from {source_count} sources")
        for source in sources:
            latest_entry = self.get_latest_entry(source)
            latest_entry_date = self.get_latest_entry_date(latest_entry)
            latest_entry_id = self.get_latest_entry_id(latest_entry)

            if latest_entry_date and not options['process_all']:
                logger.info(f'Retrieving all {source} {self.entry_name_plural} after {latest_entry_date}')
            else:
                logger.info(f'Retrieving all {source} {self.entry_name_plural}')

            try:
                new_entries = list(self.get_entries_from_source(source, since_id=latest_entry_id))
                Entry.objects.bulk_create(new_entries)
                logger.info(f"Retrieved {len(new_entries)} {self.entry_name_plural} for {source}")
            except:
                logger.exception(f"Failed to back up {source} {self.entry_name_plural}")
                failure_count += 1

        logger.info(f"All {self.entry_name_plural} backups finished. "
                    f"{source_count - failure_count} successful, {failure_count} failed.")
