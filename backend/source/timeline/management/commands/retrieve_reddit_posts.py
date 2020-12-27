import logging
from datetime import datetime
from typing import List, Tuple

import praw
import pytz
from django.db import transaction

from backup.models import RedditSource
from timeline.management.commands.retrieve_posts import BasePostRetrievalCommand
from timeline.models import Entry

logger = logging.getLogger(__name__)


class Command(BasePostRetrievalCommand):
    help = 'Retrieves reddit posts from RedditSources.'
    entry_schema = 'social.reddit.post'
    entry_name_plural = 'reddit posts'
    source_class = RedditSource

    def update_entries_from_source(self, source: source_class) -> Tuple[List[Entry], List[Entry]]:
        reddit = praw.Reddit(
            client_id=source.client_id,
            client_secret=source.client_secret,
            user_agent=source.user_agent or 'Reddit post retriever'
        )
        submissions = reddit.redditor(source.reddit_username).submissions.new(limit=None)
        updated_entries = []
        created_entries = []
        with transaction.atomic():
            for submission in submissions:
                entry, created = Entry.objects.update_or_create(
                    schema=self.entry_schema,
                    extra_attributes__post_id=submission.id,
                    defaults={
                        'title': submission.title,
                        'description': submission.selftext,
                        'date_on_timeline': datetime.fromtimestamp(submission.created_utc, pytz.UTC),
                        'extra_attributes': {
                            'post_id': submission.id,
                            'post_score': submission.score,
                            'post_community': submission.subreddit.display_name,
                            'post_user': source.reddit_username,
                            'post_url': submission.url,
                        }
                    }
                )
                if created:
                    created_entries.append(entry)
                else:
                    updated_entries.append(entry)

        return created_entries, updated_entries
