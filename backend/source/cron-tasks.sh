#!/bin/bash
source /etc/timeline-cronenv
flock --verbose -n -w 21600 /etc/cronjobs.lock sh -c "/usr/local/bin/python /usr/src/app/manage.py import; /usr/local/bin/python /usr/src/app/manage.py export"