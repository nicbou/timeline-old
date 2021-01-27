from datetime import datetime
from time import mktime
from typing import Tuple, List

import feedparser
import pytz
from django.db import models, transaction

from backup.models import BaseSource
from timeline.models import Entry


class RssSource(BaseSource):
    feed_url = models.URLField(blank=False)

    source_name = 'rss'

    def process(self) -> Tuple[int, int]:
        rss_feed = feedparser.parse(self.feed_url)

        updated_entries = []
        created_entries = []
        with transaction.atomic():
            for rss_entry in rss_feed.entries:
                entry, created = Entry.objects.update_or_create(
                    schema='social.blog.article',
                    extra_attributes__post_id=rss_entry.id,
                    extra_attributes__post_url=rss_entry.link,
                    defaults={
                        'title': rss_entry.title,
                        'source': self.entry_source,
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

        return len(created_entries), len(updated_entries)

    def __str__(self):
        return self.feed_url
