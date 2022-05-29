# Personal timeline

## Introduction

This software collects personal data (files, articles, comments, geolocation...) from different sources, and shows it on a timeline. It backs up the data it collects to remote locations. It runs on a server, and it's accessible as a website.

It's a mix of a few things:

* A photo stream
* A personal diary
* A browsable personal history
* A backup tool

There is [a longer introduction](https://nicolasbouliane.com/projects/timeline) with more screenshots on my website.

### The backend

The backend constantly imports new data from different sources (Twitter, Reddit, Google Takeout, etc). It turns the data into timeline entries, generates thumbnails, etc. It is served through a REST API.

You can also add timeline entries through the REST API. This lets you write external services that create timeline entries.

### The frontend

The frontend lets you browse your timeline day by day. It also lets you keep a daily diary.

![](https://nicolasbouliane.com/images/_ultrawide2x/Screen-Shot-2021-05-07-at-22.59.42.png)

## Setup

You need [docker](https://www.docker.com/get-started) to run this project.

0. Clone this repository.
1. Create a `.env` file, and put it in the project root (next to `docker-compose.yml`). Here's a template:
    ```
    # A long, random, secret key used by Django. You can choose any value you want.
    BACKEND_SECRET_KEY=5d41402abc4b2a...

    # A long, random, unique string used by the frontend. You can choose any value you want.
    # The frontend is an application you authorize to access the timeline API. This is the application's OAuth2 client ID.
    # This application will be created automatically for you.
    FRONTEND_CLIENT_ID=8ee2027983915e...

    # The domain where your frontend is.
    # It's required, because OAuth must redirect you *somewhere* after you log in.
    # If you are developing on localhost, use lvh.me as the domain. It's an alias for localhost.
    FRONTEND_DOMAIN=timeline.nicolasbouliane.com

    # Google Map API key used to display Google Maps in the frontend
    # How to get one: https://developers.google.com/maps/documentation/embed/get-api-key
    GOOGLE_MAPS_API_KEY=AIzaSyBdUNg8Q...

    # Two long, random, unique string used by the geolocation client. You can choose any values you want.
    # The geolocation client is an application you authorize to access the timeline API.
    # This is the application's OAuth2 client ID and client secret. This application will be created automatically for you.
    GEOLOCATION_CLIENT_ID=8ee2027983915e...
    GEOLOCATION_CLIENT_SECRET=5d41402abc4b2a...
    
    # Username and password for the MQTT client
    # OwnTracks connects to this client to log your phone's location
    MQTT_USERNAME=johntheuser
    MQTT_PASSWORD=superextrasecret
    
    # Optional. Turns on debugging for the Django backend.
    # Backend error messages are much more detailed, but can be a security risk.
    BACKEND_DEBUG=1
    
    # Optional. Sets the prefix for this project's docker images
    # Set this variable to avoid conflicts with other docker projects running on the
    # same machine.
    COMPOSE_PROJECT_NAME=timeline
    
    # Optional. Override the default docker-compose.yml file with extra docker configs
    # See `docker-compose.homeserver.yml` for an example.
    COMPOSE_FILE=docker-compose.yml:docker-compose.homeserver.yml
    ```
2. Copy your SSL certificate chain and key under `./proxy/ssl-certs`:
    - Call the cert chain `cert-chain.crt`
    - Call the key `server.key`
3. Run `docker-compose up --build -d` to build the project and start the server.
4. Create a user account by calling `scripts/timeline-create-user.sh`.
4. Access the timeline at `https://localhost` (or wherever you run your server). Log in with your user account.
5. Create new Sources and upload new Archives to see new data appear on the timeline.

If you need help setting up this project, just [email me](https://nicolasbouliane.com/contact). I don't expect this project to have many users, the documentation is not perfect.

## Entries

`/api/timeline/entries`

An Entry represents one thing that appears on the timeline. It could be a photo, a journal entry, a tweet, etc.

Entries have a `schema` attribute, like `file.document.pdf`. The schemas are read from left (general) to right (specific). The schemas determine what attributes you can expect in the `extra_attributes` field. For example, all `file.image` entries have `width` and `height` attributes.

* [List of schemas](https://github.com/nicbou/timeline/blob/master/schemas.md)

Entries also have a `source` attribute. This allows you to query entries that are related to a source. 

## Sources

`/api/source`

A Source is a source of data. Sources are suited for frequent, automatic data imports. You add a source (an API, an RSS feed, etc) to monitor, and new data is automatically imported.

For example, you can use them to automatically import photos from your phone, import your new tweets, or watch a website for new posts.

New sources can be added directly through the API. You can browse the API at `/api/source`.

### FileSystemSource

`/api/source/filesystem`

Describes a directory on the local filesystem. Entries are created from the files in that directory.

A FileSystemSource requires more initial configuration than an RsyncSource, but it saves storage space because it does not copy any files. You can use it to import large file collections, like photo albums, without using more disk space. You can use it to add a Google Drive or Dropbox directory to your timeline.

**Usage:**

1. Mount a volume under `/data/mounts` on the `timeline-backend` image. You can find an example in `docker-compose.homeserver.yml`.
2. Create a `.timelineinclude` file in the mounted volume. It lists which files will appear on the timeline. If you want all files to appear on the timeline, add two line to that file: `*` and `**/*`.
3. Create a FileSystemSource through the API.

**Required fields:**

* `key`: a unique identifier for this source (e.g. "macbook-photos")
* `path`: path of the source directory, relative to `/data/mounts`

### HackerNewsSource

`/api/source/hackernews`

Describes a source of Hacker News posts and comments.

**Required fields:**

* `key`: a unique identifier for this source (e.g. "dang")
* `hackernews_username`: The name of the Hacker News user to back up (e.g. "dang")

### RedditSource

`/api/source/reddit`

Describes a source of reddit posts and comments.

**Required fields:**

* `key`: a unique identifier for this source (e.g. "spez")
* `client_id`: Reddit API credentials
* `client_secret`: Reddit API credentials
* `user_agent`: Reddit API credentials
* `reddit_username`: The name of the Reddit user to back up (e.g. "spez")

### RssSource

`/api/source/rss`

Describes a RSS feed.

**Required fields:**

* `key`: a unique identifier for this source (e.g. "personal-blog")
* `feed_url`: The URL of the RSS feed.

### RsyncSource

`/api/source/rsync`

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

* `key`: a unique name for this source (e.g. "macbook-photos")
* `host`: hostname of the remote machine (e.g. "home.nicolasbouliane.com" or "192.168.0.123")
* `port`: SSH port on the remote machine (e.g. "22")
* `user`: SSH user on the remote machine (e.g. "backups")
* `password`: SSH password on the remote machine. This will be used to copy SSH keys. The password is never stored.
* `path`: the path to backup on the remote machine (e.g. "/home/backups")
* `key`: a unique name for this backup (e.g. "home-server")
* `key_exchange_method`: The method used to copy SSH keys to the remote host. The default (`ssh-copy-id`) works in most cases.
* `max_backups`: how many backup versions to keep. If null, old backups are never deleted. If "1", only the latest backup is kept.

### Trakt.tv

`/api/source/trakt`

Displays viewed shows and films from a [Trakt.tv](trakt.tv/) account. 

This source requires a [Trakt App to be created](https://trakt.tv/oauth/applications). (The redirect URI can be the defaul `urn:ietf:wg:oauth:2.0:oob`.)  Once created, select the app name at the site [https://trakt.tv/oauth/applications](https://trakt.tv/oauth/applications), it will display the `Client ID` and `Client Secret`. The `client_id` value is obtained from the URL (e.g. https://trakt.tv/oauth/applications/6688) has a `client_id` of 6688.

**Required fields:**

* `key`: a unique identifier for this source (e.g. "My-User-Name")
* `consumer_key`: Trakt.tv Client id
* `consumer_secret`: Trakt.tv Client secret
* `client_id`: Numerical ID of the created Trakt app

### TwitterSource

`/api/source/twitter`

Describes a source of tweets. Requires Twitter API credentials. If you can't get API credentials, upload a Twitter dump with `TwitterArchive`.

**Required fields:**

* `key`: a unique identifier for this source (e.g. "katyperry")
* `consumer_key`: Twitter API credentials
* `consumer_secret`: Twitter API credentials
* `access_token`: Twitter API credentials
* `access_token_secret`: Twitter API credentials
* `twitter_username`: The name of the Twitter user to back up, without the "@" (e.g. "katyperry")

## Archives

`/api/archive`

An archive is a source of data. Archives are for irregular, manual data imports. You upload a file or an archive, and it's turned into new Entries. For example, you can use them to import GPS logs, GDPR data exports, email dumps etc.

Unlike Sources, Archives are only processed once. After processing, original archive is preserved. 

New archives can be added directly through the API. You can browse the API at `/api/source`.

**Required fields:**

* `key`: a unique identifier for this archive (e.g. "google-takeout-2020-01-20")
* `description`: A plain text description of this archive
* `archive_files`: The archive files to process

### FacebookArchive

Imports various data from a [Facebook export](https://www.facebook.com/help/212802592074644):

* Facebook Messenger messages, including images, videos and gifs

### GoogleTakeoutArchive

`/api/archive/googletakeout`

Imports various data from a [Google Takeout export](https://takeout.google.com/).

When you create a Google Takeout archive, you must select certain export settings:

* Include all the necessary data sets:
    * "Chrome"
        * Browsing history (`activity.browsing.website`)
    * "Fit"
        * Physical activities (`activity.exercise.session`)
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

### GpxArchive

`/api/archive/gpx`

Imports a list of `activity.location` Entries from a GPX file. All points from tracks and routes are imported, and all waypoints.

### JsonArchive

`/api/archive/json`

Imports a list of Entry objects from a JSON file. It expects the same format as the API. The entries in the JSON file are imported as-is, but the `source` attribute is overridden, and the `id` attribute is ignored.

This is useful for one-off data imports. For example, I use it to process an SMS dump I found on an old hard drive.

### N26CsvArchive

`/api/n26csvarchive`

Imports transactions from an N26 CSV export.

### TelegramArchive

`/api/telegramarchive`

Imports data from the exports created by [Telegram Desktop](https://desktop.telegram.org/). Messages from channels are not imported. Messages from groups you have left are not imported.

Telegram Desktop exports its data to a folder. You must compress it into a zip file yourself. Make sure that the `result.json` file is at the root of the zip file.

**Required fields:**

* `include_group_chats`: If true, messages from group conversations will be imported. Default is true.
* `include_supergroup_chats`: If true, messages from supergroups will be imported. Default is false.

### TwitterArchive

`/api/archive/twitter`

Imports tweets from a Twitter data export.

Generally, you should import data with a `TwitterSource`, because it will keep looking for new tweets. A `TwitterArchive` is better for private accounts, or archives of deleted accounts. Unlike a `TwitterSource`, it does not require Twitter API credentials.

## Destinations

`/api/destination`

A Destination is a place where the timeline data is exported. This is how you back up your timeline.

The backups include all timeline entries, all uploaded archives, and all imported files. All data that would be lost in a crash is backed up.

The backups do not include generated assets like thumbnails. All data that can be recreated is ignored.

### RsyncDestination

`/api/destination/rsync`

It uses rsync to back up timeline entries and files to a remote filesystem. The backups are not incremental.

**Required fields:**

* `key`: a unique identifier for this destination (e.g. "rsync-cloud-backup")
* `host`: hostname of the remote machine (e.g. "home.nicolasbouliane.com")
* `port`: SSH port on the remote machine (e.g. "22")
* `user`: SSH user on the remote machine (e.g. "backups")
* `password`: SSH password on the remote machine. This will be used to copy SSH keys. The password is never stored.
* `path`: the destination path on the remote machine (e.g. "/home/backups")
* `key`: a unique name for this backup (e.g. "home-server")
* `key_exchange_method`: The method used to copy SSH keys to the remote host. The default (`ssh-copy-id`) works in most cases.

**Usage notes:**

* `path` should point to an empty directory, because anything in that directory will be overwritten by Rsync. If using Hetzner, don't set it to `./`, because it will delete the SSH keys in `./.ssh`.

## Authentication

This project does not have authentication. Everything on the timeline is public, and anyone can make destructive API requests. You will need to include your own form of authentication.

I run this software behind my home server's single sign-on.

## Geolocation

This project ships with an MQTT broker. This broker works with [OwnTracks](https://owntracks.org/) to receive geolocation pings from your phone. When your phone sends its location, a `activity.location` entry is created.
