# Schemas

This is a list of the schemas that are currently in use

## activity

### activity.browsing.search

The activity of searching the internet

- `title`: The search term
- `url`: The search URL
- `query`: The search query

### activity.browsing.video

The activity of watching a video

- `title`: Video title
- `Description`: Video description
- `mixin:previews`
- `url`: The URL of the video

### activity.browsing.website

The activity of visiting a website

- `url`: The URL of the website

### activity.location

A geolocation entry

- `mixin:coordinates`
- `source`: The source of the geolocation info (device, archive, etc)


## file

Describes a file on a filesystem.

- `mimetype`: The file's mimetype. For example "text/markdown"
- `checksum`: The file's blake2b checksum
- `path`: The file's absolute path on the filesystem
- `source`: The key of the Source that created this entry
- `backup_date`: The date of the Source backup that created this entry

### file.text

### file.document

### file.document.pdf

- `mixin:previews`: A PNG of the document's first page

### file.image

- `mixin:coordinates`
- `mixin:previews`
- `camera`: The camera's make and model.
- `creation_date`: The date on which the photo was taken. Might differ from the file's modification date.

### file.video

- `mixin:coordinates`
- `mixin:previews`
- `duration`: The duration of the video, in seconds
- `codec`
- `width`: The width of the video, in pixels
- `height`: The height of the video, in pixels


## journal

A journal entry

- `title`: Optional entry title
- `description`: The journal entry


## message

A message sent by a sender to a recipient.

### message.text.sms

- `description`: The message body
- `sender_name`: The name of the sender
- `sender_id`: The phone number of the sender
- `recipient_name`: The name of the recipient
- `recipient_id`: The phone number of the recipient


## social

Social media posts and comments

- `mixin:post`

### social.blog.article

### social.hackernews.comment

### social.hackernews.post

### social.reddit.comment

### social.reddit.post

### social.twitter.tweet

# Mixins

Mixins are common sets of attributes shared by different schemas.

## coordinates

- `location`
    - `latitude`
    - `longitude`
    - `altitude`: The altitude, in meters
    - `direction`
    - `bearing`
    - `accuracy`: The accuracy, in meters
    - `name`: The name of this location, if available

## preview

- `previews`: A dictionary of different preview sizes. The key is the name of the preview size (for example, "thumbnail"), and the value is the URL of the preview.

## post

- `description`: The post excerpt if it's available, or its full version
- `post_id`: The unique ID of the post
- `post_user`: The author of the post
- `post_thread_id`: The ID of the parent thread
- `post_parent_id`: The unique ID of the parent post (for chained comments)
- `post_body_html`: The longer, HTML version of the post
- `post_score`: The number of likes or upvotes
- `post_url`: The URL of the post
- `post_community`: The sub-community (subreddit, subforum) in which the post was made