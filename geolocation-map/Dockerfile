FROM python:slim

RUN set -ex \
	&& apt-get update && apt-get install -y --no-install-recommends \
		cron \
	&& rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY ./docker-entrypoint.sh /
COPY crontab /etc/geolocation-crontab

ENTRYPOINT ["/docker-entrypoint.sh"]