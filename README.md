# Personal timeline

This software collects my data (files, articles, comments, geolocation...) from different sources, and displays it on a timeline. It's a mix between a personal diary, a personal history, photo stream and backup tool.

## The backend

The backend routinely imports new data from different sources. The data is turned into entries that can appear on the timeline. The data sources and the timeline entries can be accessed through an API at `/api`.

## The frontend

The frontend lets you browse your timeline day by day, and keep a daily diary.

![](https://nicolasbouliane.com/images/Screenshot-2021-02-03-at-14.56.20.png)

![](https://nicolasbouliane.com/images/Screenshot-2021-02-03-at-14.53.08.png)

## Setup

You need [docker](https://www.docker.com/get-started) to run this project.

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

## General principles

The backend creates timeline entries from other sources of data. It follows these principles, in order of priority:

* Repeatable: You should be able to regenerate entries from scratch at any point. The original data must be preserved as much as possible.
* Automatic: The timeline should retrieve and show your latest data without any effort on your part.
* Fast: Performance is important, but it's not as important as the other things.

## Entries

API URL: `/api/timeline/entries`

An Entry represents one thing that appears on the timeline. It could be a photo, a journal entry, a tweet, etc.

Entries have a `schema` attribute, like `file.document.pdf`. The schemas are read from left (general) to right (specific). The schemas determine what attributes you can expect in the `extra_attributes` field. For example, all `file.image` entries have `width` and `height` attributes.

* [List of schemas](https://github.com/nicbou/timeline/blob/master/README.md)

Entries also have a `source` attribute. This allows you to query entries that are related to a source. 

## Sources

API URL: `/api/backup`

Sources are suited for frequent, automatic data imports. You add a source (an API, an RSS feed, etc) to monitor, and new data is automatically imported.

For example, you can use them to automatically import photos from your phone, import your new tweets, or watch a website for new posts.

New sources can be added directly through the API. You can browse the API at `/api/backup`.

### RsyncSource

API URL: `/api/backup/rsyncsources`

It uses rsync to synchronise files from a local or remote filesystem. RsyncSource creates incremental backups. The files in the latest backup are then turned into Entries. Files in older backups are ignored.

The backups are incremental. If you don't change any files, you can run a backup 100 times, and it won't use any bandwidth or disk space. You can limit how many old backup versions to keep with the `max_backup` option.

To exclude files from a backup, create `.rsyncignore` files on the source machine. The files listed in that file will not be backed up. It works like a `.gitignore` file.

By default, none of the files are included on the timeline. To include files on the timeline, create `.timelineinclude` files, and list the files you want to include.

Here is an example `.rsyncignore` or `.timelineinclude` file:
```
images/*.jpg
**/*.pdf
documents/invoices
```

**Required fields:**

* `host`: hostname of the remote machine (e.g. "home.nicolasbouliane.com" or "localhost")
* `port`: SSH port on the remote machine (e.g. "22")
* `user`: SSH user on the remote machine (e.g. "backups")
* `password`: SSH password on the remote machine. This will be used to copy SSH keys. The password is never stored.
* `path`: the path to backup on the remote machine (e.g. "/home/backups")
* `key`: a unique name for this backup (e.g. "home-server")
* `max_backups`: how many backup versions to keep. If null, old backups are never deleted. If "1", only the latest backup is kept.

### FileSystemSource

API URL: `/api/backup/filesystemsources`

Describes a directory on the local filesystem. Entries are created from the files in that directory.

A FileSystemSource requires more configuration than an RsyncSource, but it saves storage space because it does not copy any files. You can use it to import large file collections, like photo albums, without using more disk space.

**Usage:**

1. Mount a volume under `/srv/mounts` on the `timeline-backend` image. You can find an example in `docker-compose.homeserver.yml`.
2. Create a `.timelineinclude` file in the mounted volume. It lists which files will appear on the timeline. If you want all files to appear on the timeline, add two line to that file: `*` and `**/*`.
3. Create a FileSystemSource through the API.

**Required fields:**

* `path`: path of the source directory, relative to `/srv/mounts`

### TwitterSource

API URL: `/api/backup/twittersources`

Describes a source of tweets. Requires Twitter API credentials. If you can't get API credentials, upload a Twitter dump with `TwitterArchive`.

**Required fields:**

* `consumer_key`: Twitter API credentials
* `consumer_secret`: Twitter API credentials
* `access_token`: Twitter API credentials
* `access_token_secret`: Twitter API credentials
* `twitter_username`: The name of the Twitter user to back up, without the "@" (e.g. "nicolasbouliane")

### RedditSource

API URL: `/api/backup/redditsources`

Describes a source of reddit posts and comments.

**Required fields:**

* `client_id`: Twitter API credentials
* `client_secret`: Twitter API credentials
* `user_agent`: Twitter API credentials
* `reddit_username`: The name of the Reddit user to back up (e.g. "spez")

### HackerNewsSource

API URL: `/api/backup/hackernewssource`

Describes a source of Hacker News posts and comments.

**Required fields:**

* `hackernews_username`: The name of the Hacker News user to back up (e.g. "dang")

### RssSource

API URL: `/api/backup/rsssource`

Describes a RSS feed.

**Required fields:**

* `feed_url`: The URL of the RSS feed.

## Archives

API URL: `/api/archive`

Archives are for irregular, manual data imports. You upload a file or an archive, and it's turned into new Entries. For example, you can use them to import GPS logs, GDPR data exports, email dumps etc.

Unlike Sources, Archives are only processed once. After processing, original archive is preserved. 

New archives can be added directly through the API. You can browse the API at `/api/backup`.

### JsonArchive

API URL: `/api/archive/jsonarchives`

Imports a list of Entry objects from a JSON file. The entries in the JSON file are imported as-is, but the `source` attribute is overridden.

This is useful for one-off data imports. For example, I use it to process an SMS dump I found on an old hard drive.

### GpxArchive

API URL: `/api/archive/gpxarchives`

Imports a list of `activity.location` Entries from a GPX file. All points from tracks and routes are imported, and all waypoints.

### GoogleTakeoutArchive

API URL: `/api/archive/googletakeoutarchives`

Imports various data from a Google Takeout export:

When you create a Google Takeout archive, you must select certain export settings:

* Include all the necessary data sets:
    * "Chrome"
        * Browsing history (`activity.browsing.website`)
    * "Location History"
        * Location history (`activity.location`)
    * "My Activity" `en` `json`
        * Search history
            * Google Search
            * Google Image Search
            * Google Finance
            * Gmail
            * Google Drive
        * YouTube watch history
* Set your account language to English. The file names and data are sometimes localized.
* Set the export type to JSON whenever possible.

If you don't use these export settings, the import will not fail, but some data might not be imported.

### TwitterArchive

API URL: `/api/archive/twitterarchive`

Imports tweets from a Twitter data export.

Generally, you should import data with a `TwitterSource`, because it will keep looking for new tweets. A `TwitterArchive` is better for private accounts, or archives of deleted accounts. Unlike a `TwitterSource`, it does not require access to the Twitter API.

### N26CsvArchive

API URL: `/api/n26csvarchive`

Imports transactions from an N26 CSV export.

## Authentication

This project does not have authentication. Everything on the timeline is public, and anyone can make destructive API requests. You will need to include your own form of authentication.

I run this software behind my home server's single sign-on.

## Geolocation

This project ships with an MQTT broker. This broker works with [OwnTracks](https://owntracks.org/) to receive geolocation pings from your phone. When your phone sends its location, a `activity.location` entry is created.
