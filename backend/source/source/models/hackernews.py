import logging
from datetime import datetime, timedelta
from typing import Tuple

import pytz
import requests
from django.db import models, transaction

from source.models.source import BaseSource
from timeline.models import Entry

logger = logging.getLogger(__name__)


class HackerNewsSource(BaseSource):
    hackernews_username = models.CharField(max_length=20, blank=False)

    def process(self, force=False) -> Tuple[int, int]:
        base_schema = 'social.hackernews'

        # Hacker News entries can't be edited or deleted after 2 hours. Only look for latest entries.
        latest_entry = self.get_entries().order_by('-extra_attributes__post_id').first()
        latest_entry_date = latest_entry.date_on_timeline if latest_entry else self.date_from
        two_hours_ago = datetime.now(pytz.UTC) - timedelta(hours=2)
        after_date = min([latest_entry_date, two_hours_ago]) if latest_entry_date else None

        if latest_entry_date:
            if not self.is_date_in_date_range(latest_entry_date):
                return 0, 0
            logger.info(f'Retrieving {str(self)} entries after {after_date}')

        updated_entries = []
        created_entries = []
        with transaction.atomic():
            api_url = "https://hacker-news.firebaseio.com/v0/"
            item_ids_for_user = requests.get(f"{api_url}user/{self.hackernews_username}.json").json()['submitted']
            for item_id in item_ids_for_user:
                item = requests.get(f"{api_url}item/{item_id}.json").json()
                item_date = datetime.fromtimestamp(item['time'], pytz.UTC)
                if not self.is_date_in_date_range(item_date):
                    continue
                if after_date and item_date <= after_date:
                    break
                if item.get('deleted'):
                    continue

                entry_values = {
                    'title': item.get('title', ''),
                    'description': item.get('text', ''),
                    'date_on_timeline': item_date,
                    'extra_attributes': {
                        'post_id': item['id'],
                        'post_user': self.hackernews_username,
                        'post_score': item.get('score'),
                    }
                }

                if 'text' in item:
                    entry_values['extra_attributes']['post_body_html'] = item['text']
                if 'url' in item:
                    entry_values['extra_attributes']['post_url'] = item['url']
                if 'parent' in item:
                    entry_values['extra_attributes']['post_parent_id'] = item['parent']
                if 'score' in item:
                    entry_values['extra_attributes']['post_score'] = item['score']

                entry, created = Entry.objects.update_or_create(
                    schema=f"{base_schema}.{item['type']}",
                    source=self.entry_source,
                    extra_attributes__post_id=item['id'],
                    defaults=entry_values
                )

                if created:
                    created_entries.append(entry)
                else:
                    updated_entries.append(entry)

        return len(created_entries), len(updated_entries)

    def __str__(self):
        return f"{self.source_name}/{self.hackernews_username}"
