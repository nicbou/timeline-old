#!/bin/bash
(
 flock --verbose -n 200 || exit 1
 /usr/local/bin/python /usr/src/app/manage.py import;
 /usr/local/bin/python /usr/src/app/manage.py export;
) 200>/etc/cronjobs.lock