FROM python

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
        util-linux \
        wget \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# cron: To run the backups on a schedule
# ffmpeg: To make image and video previews
# ghostscript: To make PDF previews
# mime-support: To populate the list of mime types, and figure out file types
# netcat: To wait for the DB before starting Django
# openssh-client: To copy SSH keys to sources
# rsync: To backup files
# sshpass: To connect to ssh with a password without user interaction
# util-linux: For flock, which prevents a job from running multiple instances at once
# wget: To download more mimetypes

# https://stackoverflow.com/questions/52998331/imagemagick-security-policy-pdf-blocking-conversion
# https://askubuntu.com/questions/1181762/imagemagickconvert-im6-q16-no-images-defined
# These solutions do not work. Removing the file entirely does.
# RUN sed -i_bak 's/rights="none" pattern="PDF"/rights="read | write" pattern="PDF"/' /etc/ImageMagick-6/policy.xml
RUN rm /etc/ImageMagick-6/policy.xml

COPY requirements.txt ./
RUN pip install -r requirements.txt

# Get a longer list of mimetypes. The default IANA list is missing important ones like GPX
RUN wget https://svn.apache.org/repos/asf/httpd/httpd/branches/1.3.x/conf/mime.types -O /usr/local/etc/mime.types

COPY ssh_config /etc/ssh/ssh_config
COPY crontab /etc/timeline-crontab

RUN mkdir -p /data/mounts

# Start the backend
WORKDIR /usr/src/app
EXPOSE 80
COPY ./docker-entrypoint.sh /
ENTRYPOINT ["/docker-entrypoint.sh"]