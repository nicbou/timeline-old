# Backup tools

A web-based backend to schedule and browse backups from multiple remote machines.

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