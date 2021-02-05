#!/bin/bash
source /srv/cronenv

/usr/local/bin/python /usr/src/app/manage.py process
/usr/local/bin/python /usr/src/app/manage.py generate_previews