#!/usr/bin/env bash
set -e
set -x

scripts_dir=$(dirname "$0")
today=$(date "+%Y-%m-%d")

scp -P 2200 root@home.nicolasbouliane.com:/var/timeline/db-backups/backup-${today}.sql backup-${today}.sql
bash ${scripts_dir}/db-restore.sh backup-${today}.sql
