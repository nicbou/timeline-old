FROM python:slim

# Install dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        netcat \
        openssh-client \
        rsync \
        rsyslog \
        sshpass \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY ssh_config /etc/ssh/ssh_config

# Start the backend
WORKDIR /usr/src/app
EXPOSE 80
COPY ./docker-entrypoint.sh /
ENTRYPOINT ["/docker-entrypoint.sh"]