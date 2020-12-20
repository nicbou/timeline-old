#!/bin/bash
set -e
echo -e "\n\033[1mBacking up the database to ${1}\033[0m"
docker-compose exec db pg_dump -c -U timeline-db > "$1"
echo "Done."