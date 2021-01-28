#!/bin/bash
source /srv/cronenv

# Social media backups
/usr/local/bin/python /usr/src/app/manage.py retrieve_twitter_entries
/usr/local/bin/python /usr/src/app/manage.py retrieve_reddit_entries
/usr/local/bin/python /usr/src/app/manage.py retrieve_hackernews_entries
/usr/local/bin/python /usr/src/app/manage.py retrieve_rss_entries
/usr/local/bin/python /usr/src/app/manage.py retrieve_rsync_entries