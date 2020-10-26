FROM python:slim

# Install dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        cron \
        ffmpeg \
        ghostscript \
        imagemagick \
        mime-support \
        netcat \
        openssh-client \
        rsync \
        sshpass \
    && rm -rf /var/lib/apt/lists/*

# cron: To run the backups on a schedule
# mime-support: To populate the list of mime types, and figure out file types
# netcat: To wait for the DB before starting Django
# openssh-client: To copy SSH keys to sources
# rsync: To backup files
# rsyslog: To log everything

# https://stackoverflow.com/questions/52998331/imagemagick-security-policy-pdf-blocking-conversion
RUN sed -i '/disable ghostscript format types/,+6d' /etc/ImageMagick-6/policy.xml 

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY ssh_config /etc/ssh/ssh_config
COPY crontab /srv/crontab

# Start the backend
WORKDIR /usr/src/app
EXPOSE 80
COPY ./docker-entrypoint.sh /
ENTRYPOINT ["/docker-entrypoint.sh"]