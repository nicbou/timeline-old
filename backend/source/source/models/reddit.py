from datetime import datetime
from typing import Tuple, List

import praw as praw
import pytz
from django.db import models, transaction

from source.models.source import BaseSource
from timeline.models import Entry


class RedditSource(BaseSource):
    client_id = models.CharField(max_length=50, blank=False)
    client_secret = models.CharField(max_length=50, blank=False)
    user_agent = models.CharField(max_length=100, blank=True)
    reddit_username = models.CharField(max_length=20, blank=False)

    def process(self, force=False) -> Tuple[int, int]:
        created_posts, updated_posts = self.process_posts()
        created_comments, updated_comments = self.process_comments()
        return len(created_posts) + len(created_comments), len(updated_posts) + len(updated_comments)

    def process_posts(self) -> Tuple[List[Entry], List[Entry]]:
        reddit = praw.Reddit(
            client_id=self.client_id,
            client_secret=self.client_secret,
            user_agent=self.user_agent or 'Reddit post retriever'
        )
        submissions = reddit.redditor(self.reddit_username).submissions.new(limit=None)
        updated_entries = []
        created_entries = []
        with transaction.atomic():
            for submission in submissions:
                date_on_timeline = datetime.fromtimestamp(submission.created_utc, pytz.UTC)
                if self.is_date_in_date_range(date_on_timeline):
                    entry, created = Entry.objects.update_or_create(
                        schema='social.reddit.post',
                        extra_attributes__post_id=submission.id,
                        defaults={
                            'title': submission.title,
                            'description': submission.selftext,
                            'source': self.entry_source,
                            'date_on_timeline': date_on_timeline,
                            'extra_attributes': {
                                'post_id': submission.id,
                                'post_score': submission.score,
                                'post_community': submission.subreddit.display_name,
                                'post_user': self.reddit_username,
                                'post_url': submission.url,
                            }
                        }
                    )
                    if created:
                        created_entries.append(entry)
                    else:
                        updated_entries.append(entry)

        return created_entries, updated_entries

    def process_comments(self) -> Tuple[List[Entry], List[Entry]]:
        reddit = praw.Reddit(
            client_id=self.client_id,
            client_secret=self.client_secret,
            user_agent=self.user_agent or 'Reddit comment retriever'
        )
        comments = reddit.redditor(self.reddit_username).comments.new(limit=None)
        updated_entries = []
        created_entries = []
        with transaction.atomic():
            for comment in comments:
                entry, created = Entry.objects.update_or_create(
                    schema='social.reddit.comment',
                    extra_attributes__post_id=comment.id,
                    defaults={
                        'title': '',
                        'description': comment.body,
                        'source': self.entry_source,
                        'date_on_timeline': datetime.fromtimestamp(comment.created_utc, pytz.UTC),
                        'extra_attributes': {
                            'post_id': comment.id,
                            'post_score': comment.score,
                            'post_body_html': comment.body_html,
                            'post_parent_id': comment.parent_id,
                            'post_thread_id': comment.submission.id,
                            'post_community': comment.subreddit.display_name,
                            'post_user': self.reddit_username,
                        }
                    }
                )
                if created:
                    created_entries.append(entry)
                else:
                    updated_entries.append(entry)

        return created_entries, updated_entries
