#!/bin/bash

# Wait for database
until nc -z db 5432; do echo Waiting for PostgreSQL; sleep 1; done

python manage.py migrate                  # Apply database migrations
python manage.py collectstatic --noinput  # Collect static files

# Prepare log files and start outputting logs to stdout
mkdir -p /var/log/backend
touch /var/log/backend/gunicorn.log
touch /var/log/backend/access.log
touch /var/log/backend/cron.log
tail -n 0 -f /var/log/backend/*.log &
service rsyslog start

# Start Gunicorn processes
echo Starting Gunicorn.
exec gunicorn backend.wsgi:application \
    --name backend \
    --reload \
    --bind 0.0.0.0:80 \
    --workers 3 \
    --log-level=info \
    --log-file=/var/log/backend/gunicorn.log \
    --access-logfile=/var/log/backend/access.log \
    "$@"
