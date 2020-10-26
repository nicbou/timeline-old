#!/bin/bash
docker-compose exec backend python manage.py run_backups \
&& docker-compose exec backend python manage.py generate_backup_entries \
&& docker-compose exec backend python manage.py process_file_entries \