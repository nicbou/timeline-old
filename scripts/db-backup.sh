#!/bin/bash
set -e
echo -e "\n\033[1mBacking up the database to ${1}\033[0m"
docker exec -t $(docker-compose ps -q timeline-db) pg_dump --if-exists --clean --create -U postgres -f /tmp/db-dump.sql timeline
docker cp $(docker-compose ps -q timeline-db):/tmp/db-dump.sql "$1"
docker exec -t $(docker-compose ps -q timeline-db) rm /tmp/db-dump.sql
echo "Done."
