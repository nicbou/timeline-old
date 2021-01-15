#!/bin/bash
set -e
echo -e "\n\033[1mBacking up the database to ${1}\033[0m"
docker-compose exec timeline-db pg_dump -c -U postgres > "$1"
echo "Done."
