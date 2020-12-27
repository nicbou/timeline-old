import logging
from typing import List

from django.core.management.base import BaseCommand

from backup.models import RssSource
from timeline.management.commands.retrieve_posts import BasePostRetrievalCommand
from timeline.models import Entry

logger = logging.getLogger(__name__)


class RssRetrievalCommand(BasePostRetrievalCommand):
    entry_name_plural = 'entries'
    source_class = RssSource

    def update_entries_from_source(self, source: source_class) -> List[Entry]:
        raise NotImplementedError
