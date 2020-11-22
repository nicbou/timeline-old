#!/bin/bash
docker-compose exec timeline-backend python manage.py run_rsync_backups \
&& docker-compose exec timeline-backend python manage.py generate_backup_entries \
&& docker-compose exec timeline-backend python manage.py process_file_entries
