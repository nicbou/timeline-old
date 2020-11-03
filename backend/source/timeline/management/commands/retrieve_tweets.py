import logging
from typing import List

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

    def get_entries_from_source(self, source, since_id=None) -> List[Entry]:
        auth = tweepy.OAuthHandler(source.consumer_key, source.consumer_secret)
        auth.set_access_token(source.access_token, source.access_token_secret)
        api = tweepy.API(auth)
        cursor = tweepy.Cursor(
            api.user_timeline,
            screen_name=f'@{source.twitter_username}',
            tweet_mode='extended',
            since_id=since_id,
        ).items()

        for tweet in cursor:
            entry = Entry(
                schema=self.entry_schema,
                title='',
                description=tweet.full_text,
                date_on_timeline=tweet.created_at,
                extra_attributes={
                    'post_id': tweet.id,
                    'post_user': source.twitter_username,
                }
            )
            if tweet.coordinates:
                entry.extra_attributes['location'] = {
                    'latitude': tweet.coordinates[0],
                    'longitude': tweet.coordinates[1],
                }
            yield entry

    def get_latest_entry(self, source) -> Entry:
        return Entry.objects \
            .filter(extra_attributes__post_user=source.twitter_username, schema=self.entry_schema) \
            .order_by('-extra_attributes__post_id') \
            .first()
