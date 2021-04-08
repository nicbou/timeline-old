#!/bin/bash
source /etc/timeline-cronenv

/usr/local/bin/python /usr/src/app/manage.py process
/usr/local/bin/python /usr/src/app/manage.py generate_previews