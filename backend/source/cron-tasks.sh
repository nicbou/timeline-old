#!/bin/bash
(
 flock --verbose -n 200 || exit 1;
 source /etc/timeline-cronenv;
 /usr/local/bin/python /usr/src/app/manage.py import > /tmp/stdout 2>&1;
 /usr/local/bin/python /usr/src/app/manage.py export > /tmp/stdout 2>&1;
) 200>/etc/cronjobs.lock