#!/bin/bash
source /srv/cronenv

# Social media backups
/usr/local/bin/python /usr/src/app/manage.py retrieve_twitter_tweets
/usr/local/bin/python /usr/src/app/manage.py retrieve_reddit_comments
/usr/local/bin/python /usr/src/app/manage.py retrieve_reddit_posts
/usr/local/bin/python /usr/src/app/manage.py retrieve_hackernews_items

# File backups
/usr/local/bin/python /usr/src/app/manage.py run_rsync_backups &&
/usr/local/bin/python /usr/src/app/manage.py generate_backup_entries &&
/usr/local/bin/python /usr/src/app/manage.py process_file_entries