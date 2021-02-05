#!/bin/bash
docker-compose exec timeline-backend python manage.py generate_previews $@
