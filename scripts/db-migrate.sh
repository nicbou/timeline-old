#!/bin/bash
docker-compose exec timeline-backend python manage.py makemigrations && docker-compose exec timeline-backend python manage.py migrate
