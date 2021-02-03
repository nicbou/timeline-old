# Personal timeline

This software collects personal data from different sources, and displays it on a personal timeline. It's like the timeline in your photos app, but for more than just photos.

The timeline is meant to be extended with all sorts of data: geolocation, social media posts, blog posts, journal entries etc.

## Setup

1. Create a `.env` file with the following variables:
```
# A long, random, secret key used by Django
BACKEND_SECRET_KEY=...

# Optional. Turns on debugging for the Django backend
BACKEND_DEBUG=1

# Username and password for the MQTT client
# OwnTracks connects to this client to log the phone's location
MQTT_USERNAME=johntheuser
MQTT_PASSWORD=superextrasecret

# Optional. Sets the prefix for this project's docker images
COMPOSE_PROJECT_NAME=timeline

# Optional. Overrides the default docker-compose.yml file with your extra configs
COMPOSE_FILE=docker-compose.yml:docker-compose.homeserver.yml
```

2. Copy your SSL certificate chain and key under `./proxy/ssl-certs`:
    - Call the cert chain `cert-chain.crt`
    - Call the key `server.key`
3. Run `docker-compose up --build -d` to start the server.

## Entries

An Entry represents one thing that appears on the timeline. It could be a photo, a journal entry, a tweet, etc.

Entries have a `schema` attribute, like `file.document.pdf`. The schemas are read from left (general) to right (specific). The schemas determine what attributes you can expect in the `extra_attributes` field. For example, all `file.image` entries have `width` and `height` attributes.

## Sources

Sources describe a regular source of data. For example, a daily backup, a social media feed or a blog. Sources are monitored for changes, and new data is automatically imported.

Sources are suited for frequent, automatic data imports.

New sources can be added directly through the API. You can browse the API at `/api/backup`.

### RsyncSource

A remote machine that will be backed up with rsync. When you create the source, you must supply a password. This will be used to copy SSH keys. the password will not be stored.

**Required fields:**

* `host`: hostname of the remote machine (e.g. "home.nicolasbouliane.com")
* `port`: SSH port on the remote machine (e.g. "22")
* `user`: SSH user on the remote machine (e.g. "backups")
* `path`: the path to backup on the remote machine (e.g. "/home/backups")
* `key`: a unique name for this backup (e.g. "home-server")

The backups are incremental. If you don't change any files, you can run a backup 100 times, and it won't use any extra bandwidth or disk space.

To exclude files from a backup, create `.rsyncignore` files on the source machine. The files listed in that file will not be backed up. It's a bit like a `.gitignore` file.

To back up files, but exclude them from the timeline, create `.timelineinclude` files on the source machine. If a file is not in the `.timelineinclude` file, it won't appear on the timeline.

Here is an example `.rsyncignore` or `.timelineinclude` file:
```
images/*.jpg
**/*.pdf
documents/invoices
```

### TwitterSource

Describes a source of tweets.

**Required fields:**

* `consumer_key`: Twitter API credentials
* `consumer_secret`: Twitter API credentials
* `access_token`: Twitter API credentials
* `access_token_secret`: Twitter API credentials
* `twitter_username`: The name of the Twitter user to back up, without the "@" (e.g. "nicolasbouliane")

### RedditSource

Describes a source of reddit posts and comments.

**Required fields:**

* `client_id`: Twitter API credentials
* `client_secret`: Twitter API credentials
* `user_agent`: Twitter API credentials
* `reddit_username`: The name of the Reddit user to back up (e.g. "spez")

### HackerNewsSource

Describes a source of Hacker News posts and comments.

**Required fields:**

* `hackernews_username`: The name of the Hacker News user to back up (e.g. "dang")

### RssSource

Describes a RSS feed.

**Required fields:**

* `feed_url`: The URL of the RSS feed.

## Archives

Archives describe a source of data that will not change. For example, an email archive, a personal data export, or an archive of your text messages. Archives are not monitored for changes, and the data is only imported once.

Archives are suited for irregular, manual data imports.

An Archive instance contains information about how to retrieve the archive.

### GoogleTakeoutArchive

Imports various data from a Google Takeout export

* Location history
* Google Chrome browsing history

### TwitterArchive

Imports tweets from a Twitter data export.

Generally, you should import data with a `TwitterSource`, because it will keep looking for new tweets. A `TwitterArchive` is better for private accounts, or archives of deleted accounts. Unlike a `TwitterSource`, it does not require access to the Twitter API.

## Authentication

This project does not have authentication. Everything on the timeline is public, and anyone can make destructive API requests. You will need to include your own form of authentication.

I run this software behind my home server's single sign-on.

## Geolocation

This project ships with an MQTT broker. This broker works with [OwnTracks](https://owntracks.org/) to receive geolocation pings from your phone. When your phone sends its location, a `activity.location` entry is created.