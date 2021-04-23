#!/bin/bash
source /etc/timeline-cronenv

/usr/local/bin/python /usr/src/app/manage.py import
/usr/local/bin/python /usr/src/app/manage.py export