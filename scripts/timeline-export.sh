#!/bin/bash
docker-compose exec timeline-backend python manage.py export $@
