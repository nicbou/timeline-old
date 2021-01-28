#!/bin/bash
# Retrieves posts from social media sources
docker-compose exec timeline-backend python manage.py retrieve_reddit_entries \
&& docker-compose exec timeline-backend python manage.py retrieve_twitter_entries \
&& docker-compose exec timeline-backend python manage.py retrieve_hackernews_entries \
&& docker-compose exec timeline-backend python manage.py retrieve_rss_entries
