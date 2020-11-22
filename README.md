# Backup tools

A web-based app to collect various sorts of personal data (rsync backups, social media activity, etc) and display it as a personal timeline.

The timeline was designed to be extended with all sorts of entries: geolocation, social media posts, blog posts, journal entries etc. It is meant to be a person's complete timeline.

## Setup

1. Create a `.env` file with the following variables:
```
# A long, random, secret key used by Django
BACKEND_SECRET_KEY=...

# Optional. Enables debugging.
BACKEND_DEBUG=1

# Optional. Sets the prefix for this project's docker images.
COMPOSE_PROJECT_NAME=timeline

# Optional. Overrides the default docker-compose.yml file with your extra configs
COMPOSE_FILE=docker-compose.yml:docker-compose.homeserver.yml
```

2. Copy your SSL certificate chain and key under `./proxy/ssl-certs`:
    - Call the cert chain `cert-chain.crt`
    - Call the key `server.key`
3. Run `docker-compose up --build -d` to start the server.

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

### Authentication

This project is not shipped with authentication, because it runs behind's my home server's single sign-on. You could trivially add authentication to Django Rest Framework, but you would also need to make the frontend use that authentication.