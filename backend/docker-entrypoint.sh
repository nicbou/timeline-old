#!/bin/bash

# Wait for database
until nc -z timeline-db 5432; do echo Waiting for PostgreSQL; sleep 1; done

python manage.py migrate                  # Apply database migrations
python manage.py collectstatic --noinput  # Collect static files

# Prepare log files and start outputting logs to stdout
mkdir -p /var/log/backend
touch /var/log/backend/gunicorn.log
touch /var/log/backend/access.log
tail -n 0 -f /var/log/backend/*.log &

# Activate cron with all Django environment variables
> /etc/timeline-cronenv
printf "export BACKEND_SECRET_KEY=%q\n" "${BACKEND_SECRET_KEY}" >> /etc/timeline-cronenv
printf "export BACKEND_DEBUG=%q\n" "${BACKEND_DEBUG}" >> /etc/timeline-cronenv

mkfifo /tmp/stdout /tmp/stderr
chmod 0666 /tmp/stdout /tmp/stderr
tail -f /tmp/stdout &
tail -f /tmp/stderr >&2 &

crontab /etc/timeline-crontab
service cron start

# Start Gunicorn processes
echo Starting Gunicorn.
exec gunicorn backend.wsgi:application \
    --name backend \
    --timeout 1200 \
    --reload \
    --bind 0.0.0.0:80 \
    --workers 3 \
    --log-level=info \
    --log-file=/var/log/backend/gunicorn.log \
    --access-logfile=/var/log/backend/access.log \
    "$@"
