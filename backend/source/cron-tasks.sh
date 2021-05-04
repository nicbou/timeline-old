#!/bin/bash
function logline {
    echo -e -n "\x1b[32m`date +'%Y-%m-%d %H:%M:%S'` \x1b[90mINFO \x1b[93m[cron-tasks.sh]\x1b[0m "
    echo $1
}

logline "Running cron-tasks.sh..."

# flock prevents multiple instances of this script from running at the same time
(
 flock -n 200 || exit 111;
 source /etc/timeline-cronenv;
 /usr/local/bin/python /usr/src/app/manage.py import > /tmp/stdout 2>&1;
 /usr/local/bin/python /usr/src/app/manage.py export > /tmp/stdout 2>&1;
) 200>/etc/cronjobs.lock

exit_code=$?
if [ $exit_code -ne 0 ]; then
    if [ $exit_code -eq 111 ]; then
        logline "cron-tasks.sh did not run - another instance is already running"
    else
        logline "cron-tasks.sh failed - exit code was ${exit_code}"
    fi
else
    logline "cron-tasks.sh finished without errors"
fi
