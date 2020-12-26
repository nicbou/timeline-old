import logging
from datetime import datetime, timedelta
from typing import List, Tuple

import pytz as pytz
import requests
from django.db import transaction

from backup.models import HackerNewsSource
from timeline.management.commands.retrieve_posts import BasePostRetrievalCommand
from timeline.models import Entry

logger = logging.getLogger(__name__)


class Command(BasePostRetrievalCommand):
    help = 'Retrieves comments and posts from Hacker News'
    base_entry_schema = 'social.hackernews'
    entry_name_plural = 'posts and comments'
    source_class = HackerNewsSource

    def update_entries_from_source(self, source: source_class) -> Tuple[List[Entry], List[Entry]]:
        latest_entry = self.get_latest_entry(source)
        latest_entry_date = latest_entry.date_on_timeline if latest_entry else None
        two_hours_ago = datetime.now(pytz.UTC) - timedelta(hours=2)
        after_date = min([latest_entry_date, two_hours_ago]) if latest_entry_date else None

        if latest_entry_date:
            logger.info(f'Retrieving all {source} {self.entry_name_plural} after {after_date}')
        else:
            logger.info(f'Retrieving all {source} {self.entry_name_plural}')

        updated_entries = []
        created_entries = []
        with transaction.atomic():
            for item_id in self.get_item_ids_for_user(source.hackernews_username):
                item = self.get_item_for_id(item_id)
                item_date = datetime.fromtimestamp(item['time'], pytz.UTC)
                if after_date and item_date <= after_date:
                    break

                entry_values = {
                    'title': item.get('title', ''),
                    'description': item.get('text', ''),
                    'date_on_timeline': item_date,
                    'extra_attributes': {
                        'post_user': source.hackernews_username,
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
                    schema=f"{self.base_entry_schema}.{item['type']}",
                    extra_attributes__post_id=item['id'],
                    defaults=entry_values
                )

                if created:
                    created_entries.append(entry)
                else:
                    updated_entries.append(entry)

        return created_entries, updated_entries

    def get_item_for_id(self, item_id: int) -> dict:
        return requests.get(f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json?print=pretty").json()

    def get_item_ids_for_user(self, username: str) -> List[int]:
        return requests.get(f"https://hacker-news.firebaseio.com/v0/user/{username}.json").json()['submitted']

    def get_latest_entry(self, source) -> Entry:
        return Entry.objects \
            .filter(
                extra_attributes__post_user=source.hackernews_username,
                schema__startswith=f"{self.base_entry_schema}."
            ) \
            .order_by('-extra_attributes__post_id') \
            .first()
