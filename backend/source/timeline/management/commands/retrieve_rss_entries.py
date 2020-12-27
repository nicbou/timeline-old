import logging
from datetime import datetime
from time import mktime
from typing import List, Tuple

import feedparser
import pytz
from django.db import transaction

from backup.models import RssSource
from timeline.management.commands.retrieve_posts import BasePostRetrievalCommand
from timeline.models import Entry

logger = logging.getLogger(__name__)


class Command(BasePostRetrievalCommand):
    entry_name_plural = 'RSS entries'
    entry_schema = 'social.blog.article'
    source_class = RssSource

    def update_entries_from_source(self, source: source_class) -> Tuple[List[Entry], List[Entry]]:
        rss_feed = feedparser.parse(source.feed_url)

        updated_entries = []
        created_entries = []
        with transaction.atomic():
            for rss_entry in rss_feed.entries:
                entry, created = Entry.objects.update_or_create(
                    schema=self.entry_schema,
                    extra_attributes__post_id=rss_entry.id,
                    extra_attributes__post_url=rss_entry.link,
                    defaults={
                        'title': rss_entry.title,
                        'description': rss_entry.summary,
                        'date_on_timeline': datetime.fromtimestamp(mktime(rss_entry.published_parsed), pytz.UTC),
                        'extra_attributes': {
                            'post_id': rss_entry.id,
                            'post_url': rss_entry.link,
                            'post_user': rss_entry.author,
                            'post_body_html': rss_entry.description or rss_entry.summary,
                        }
                    }
                )
                if created:
                    created_entries.append(entry)
                else:
                    updated_entries.append(entry)

        return created_entries, updated_entries
