import logging
from typing import Tuple

import pytz
import tweepy as tweepy
from django.db import models, transaction

from source.models.source import BaseSource
from timeline.models import Entry

logger = logging.getLogger(__name__)


class TwitterSource(BaseSource):
    consumer_key = models.CharField(max_length=50, blank=False)
    consumer_secret = models.CharField(max_length=50, blank=False)
    access_token = models.CharField(max_length=50, blank=False)
    access_token_secret = models.CharField(max_length=50, blank=False)
    twitter_username = models.CharField(max_length=50, blank=False)

    def process(self, force=False) -> Tuple[int, int]:
        auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        auth.set_access_token(self.access_token, self.access_token_secret)
        api = tweepy.API(auth)

        schema = 'social.twitter.tweet'
        latest_entry = Entry.objects \
            .filter(source=self.entry_source)\
            .order_by('-extra_attributes__post_id')\
            .first()
        latest_entry_date = latest_entry.date_on_timeline if latest_entry else self.date_from
        latest_entry_id = latest_entry.extra_attributes.get('post_id') if latest_entry else None

        if latest_entry_date:
            if not self.is_date_in_date_range(latest_entry_date):
                return 0, 0
            logger.info(f'Retrieving all {self} tweets after {latest_entry_date}')
        else:
            logger.info(f'Retrieving all {self} tweets')

        cursor = tweepy.Cursor(
            api.user_timeline,
            screen_name=f'@{self.twitter_username}',
            tweet_mode='extended',
            since=self.date_from,
            until=self.date_until,
            since_id=latest_entry_id,
        ).items()

        updated_entries = []
        created_entries = []
        with transaction.atomic():
            for tweet in cursor:
                defaults = {
                    'title': '',
                    'description': tweet.full_text,
                    'date_on_timeline': pytz.utc.localize(tweet.created_at),
                    'extra_attributes': {
                        'post_id': tweet.id,
                        'post_user': self.twitter_username,
                    }
                }

                if tweet.in_reply_to_status_id:
                    defaults['extra_attributes']['post_parent_id'] = tweet.in_reply_to_status_id

                entry, created = Entry.objects.update_or_create(
                    schema=schema,
                    source=self.entry_source,
                    extra_attributes__post_id=tweet.id,
                    defaults=defaults,
                )

                if created:
                    created_entries.append(entry)
                else:
                    updated_entries.append(entry)

        return len(created_entries), len(updated_entries)
