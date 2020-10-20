FROM python:slim

# Install dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        netcat \
        rsyslog \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install -r requirements.txt

# Install backup scripts
ENV PATH="/usr/src/scripts:${PATH}"

# Start the backend
WORKDIR /usr/src/app
EXPOSE 80
COPY ./docker-entrypoint.sh /
ENTRYPOINT ["/docker-entrypoint.sh"]