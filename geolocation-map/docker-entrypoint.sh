#!/bin/bash

crontab /etc/geolocation-crontab
service cron start

python -m http.server 80 -d "/var/www"