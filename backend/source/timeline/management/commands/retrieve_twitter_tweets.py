import logging
from typing import List, Tuple

import tweepy

from backup.models import TwitterSource
from timeline.management.commands.retrieve_posts import BasePostRetrievalCommand
from timeline.models import Entry

logger = logging.getLogger(__name__)


class Command(BasePostRetrievalCommand):
    help = 'Retrieves tweets from TweetSources.'
    entry_schema = 'social.twitter.tweet'
    entry_name_plural = 'tweets'
    source_class = TwitterSource

    def update_entries_from_source(self, source: source_class) -> Tuple[List[Entry], List[Entry]]:
        auth = tweepy.OAuthHandler(source.consumer_key, source.consumer_secret)
        auth.set_access_token(source.access_token, source.access_token_secret)
        api = tweepy.API(auth)

        latest_entry = self.get_latest_entry(source)
        latest_entry_date = latest_entry.date_on_timeline if latest_entry else None
        latest_entry_id = latest_entry.extra_attributes.get('post_id') if latest_entry else None

        if latest_entry_date:
            logger.info(f'Retrieving all {source} {self.entry_name_plural} after {latest_entry_date}')
        else:
            logger.info(f'Retrieving all {source} {self.entry_name_plural}')

        cursor = tweepy.Cursor(
            api.user_timeline,
            screen_name=f'@{source.twitter_username}',
            tweet_mode='extended',
            since_id=latest_entry_id,
        ).items()

        updated_entries = []
        created_entries = []
        for tweet in cursor:
            entry, created = Entry.objects.update_or_create(
                schema=self.entry_schema,
                extra_attributes__post_id=tweet.id,
                defaults={
                    'title': '',
                    'description': tweet.full_text,
                    'date_on_timeline': tweet.created_at,
                    'extra_attributes': {
                        'post_id': tweet.id,
                        'post_user': source.twitter_username,
                    }
                }
            )
            if tweet.coordinates:
                entry.extra_attributes['location'] = {
                    'latitude': tweet.coordinates[0],
                    'longitude': tweet.coordinates[1],
                }

            if created:
                created_entries.append(entry)
            else:
                updated_entries.append(entry)

        return created_entries, updated_entries

    def get_latest_entry(self, source) -> Entry:
        return Entry.objects \
            .filter(extra_attributes__post_user=source.twitter_username, schema=self.entry_schema) \
            .order_by('-extra_attributes__post_id') \
            .first()
