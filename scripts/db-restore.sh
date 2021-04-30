#!/bin/bash
set -e
echo -e "\n\033[1mRestoring database from ${1}\033[0m"
cat "$1" | docker-compose exec -T timeline-db psql -U postgres
echo "Done."
