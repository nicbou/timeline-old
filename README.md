# Backup tools

A web-based app to schedule, browse and manage backups from multiple remote machines. Shows the backed up file on a web-based timeline.

Basically, it's rsync with an API and a fancy GUI.

## Setup

1. Create a `.env` file with the following variables:
```
# A long, random, secret key used by Django
BACKEND_SECRET_KEY=...

# Optional. Enables debugging.
BACKEND_DEBUG=1

# Optional. Sets the prefix for this project's docker images.
COMPOSE_PROJECT_NAME=timeline
```

2. Run `docker-compose up --build -d` to start the server.

## Backing up Sources

Use the API to add new sources. The supplied password will be used to copy SSH keys on the Source server. The password is not saved.

Once added, Sources are backed up automatically using `rsync`. The backups are incremental. The files are only transferred once, unless they change.

You can force a new backup by calling `scripts/run_backups.sh`. It will back up all the Sources.

You can create `.rsyncignore` files on the Source filesystem to exclude files from the backup. It works like a `.gitignore` file.

You can create `.timelineinclude` files on the Source filesystem to include files in the timeline. Each line is a glob pattern that matches files in the backup.

Example `.rsyncignore` or `.timelineinclude` file:
```
.git
.DS_Store
__pycache__
*.iso
images/icons
```