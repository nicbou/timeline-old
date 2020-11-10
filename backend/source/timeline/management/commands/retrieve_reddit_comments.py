import logging
from datetime import datetime
from typing import List

import praw
import pytz

from backup.models import RedditSource
from timeline.management.commands.retrieve_posts import BasePostRetrievalCommand
from timeline.models import Entry

logger = logging.getLogger(__name__)


class Command(BasePostRetrievalCommand):
    help = 'Retrieves reddit comments from RedditSources.'
    entry_schema = 'social.reddit.comment'
    entry_name_plural = 'reddit comments'
    source_class = RedditSource

    def update_entries_from_source(self, source: source_class) -> List[Entry]:
        reddit = praw.Reddit(
            client_id=source.client_id,
            client_secret=source.client_secret,
            user_agent=source.user_agent or 'Reddit comment retriever'
        )
        comments = reddit.redditor(source.reddit_username).comments.new(limit=None)
        updated_entries = []
        created_entries = []
        for comment in comments:
            entry, created = Entry.objects.update_or_create(
                schema=self.entry_schema,
                extra_attributes__post_id=comment.id,
                defaults={
                    'title': '',
                    'description': comment.body,
                    'date_on_timeline': datetime.fromtimestamp(comment.created_utc, pytz.UTC),
                    'extra_attributes': {
                        'post_id': comment.id,
                        'post_score': comment.score,
                        'post_body_html': comment.body_html,
                        'post_parent_id': comment.parent_id,
                        'post_thread_id': comment.submission.id,
                        'post_community': comment.subreddit.display_name,
                        'post_user': source.reddit_username,
                    }
                }
            )
            if created:
                created_entries.append(entry)
            else:
                updated_entries.append(entry)

        return created_entries, updated_entries
