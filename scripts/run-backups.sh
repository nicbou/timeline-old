#!/bin/bash
docker-compose exec timeline-backend python manage.py retrieve_rsync_entries && docker-compose exec timeline-backend python manage.py create_previews
