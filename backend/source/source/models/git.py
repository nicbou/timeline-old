from datetime import timedelta
from typing import Tuple
from urllib.parse import urlparse

import pytz
from django.db import models, transaction
from pydriller import Repository

from source.models.source import BaseSource
from timeline.models import Entry


class GitSource(BaseSource):
    repo_url = models.URLField(blank=False)
    author_name = models.CharField(max_length=200, null=True)

    def get_repo_url(self):
        if urlparse(self.repo_url).netloc == 'github.com':
            return self.repo_url.rsplit('.', 1)[0]  # Remove the .git extension
        return self.repo_url

    def get_repo_name(self):
        parsed_url = urlparse(self.repo_url)
        if parsed_url.netloc == 'github.com':
            return parsed_url.path.rsplit('.', 1)[0].strip('/')  # e.g. "nicbou/timeline"

    def get_commit_url(self, commit):
        if urlparse(self.repo_url).netloc == 'github.com':
            return f"{self.repo_url.rsplit('.', 1)[0]}/commit/{commit.hash}"

    @transaction.atomic
    def process(self, force=False) -> Tuple[int, int]:
        filters = {}
        if self.author_name:
            filters['only_authors'] = [self.author_name, ]

        if self.date_from:
            filters['since'] = self.date_from - timedelta(seconds=1)
        if self.date_until:
            filters['to'] = self.date_until + timedelta(seconds=1)

        commits = Repository(self.repo_url, **filters).traverse_commits()

        self.get_entries().delete()

        entries_to_create = []
        for commit in commits:
            entries_to_create.append(Entry(
                title=commit.msg,
                description=commit.hash,
                date_on_timeline=commit.committer_date.astimezone(pytz.UTC),
                schema='commit',
                source=self.entry_source,
                extra_attributes={
                    'hash': commit.hash,
                    'url': self.get_commit_url(commit),
                    'author': {
                        'email': commit.author.email,
                        'name': commit.author.name,
                    },
                    'changes': {
                        'files': commit.files,
                        'insertions': commit.insertions,
                        'deletions': commit.deletions,
                    },
                    'repo': {
                        'name': self.get_repo_name() or commit.project_name,
                        'url': self.get_repo_url(),
                    },
                }
            ))
        Entry.objects.bulk_create(entries_to_create)
        return len(entries_to_create), 0
