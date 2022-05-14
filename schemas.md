# Schemas

This is a list of the schemas that are currently in use

## *

- `title`
- `description`
- `source`: the source or archive that created this entry. For example, "RsyncSource/bedroom-pc".
- `schema`: the schema of this entry
- `date_on_timeline`: the date this entry will appear on the timeline

## activity

### activity.browsing.search

The activity of searching the internet

- `title`: Search term
- `url`: Search URL

### activity.browsing.video

The activity of watching a video

- `title`: Video title
- `description`: Video description
- `mixin:file`
- `mixin:previews`
- `url`: The URL of the video

### activity.watching.movie

The activity of watching a movie

- `title`: Movie title
- `description`: Movie description
- `url`: The URL of the movie in Trakt
- `trakt_event_id`: Unique Trakt ID for this watched event
- `trakt_id`: Trakt ID for the movie
- `year`: Movie release year

### activity.watching.show

The activity of watching an episode of a show

- `title`: Episode title
- `description`: Episode description
- `url`: The URL of the episode in Trakt
- `trakt_event_id`: Unique Trakt ID for this watched event
- `episode`: Episode information
- `episode:name`
- `episode:season`
- `episode:number`: episode number within season
- `episode:trakt_id`: Trakt ID for the episode
- `episode:trakt_slug`: Trakt slug for the episode
- `show`: show information
- `show:name` 
- `show:year`
- `show:trakt_id`: Trakt ID for the show
- `show:trakt_slug`: Trakt slug for the show

### activity.browsing.website

The activity of visiting a page on a website

- `title`: Webpage title
- `url`: Webpage URL

### activity.location

The user's geolocation at that time.

- `description`: Text description, such as messages sent by a GPS beacon.
- `mixin:location`

### activity.exercise.session

A physical activity session. Can be composed of different segments within itself, but will be the main activity feature. 

For example, during a mixed martial arts session, there was also a period of boxing, and a period of running. This will show up only as `Mixed martial arts`, but can contain unexpected elements such as `step counter` due to the running activity.

- `title`: Type of physical activity
- `duration`: Duration of activity, in seconds
- `heart_minutes`: Google 'heart minutes'. The number of Heart Points earned depends on the intensity of the activity. See google documentation to calculate Heart Points.
- `calories`: The total calories (in kilocalories) burned by the user, including calories burned at rest (BMR).
- `step_count`
- `distance`: Distance covered, in meters
- `speed`: Average speed over the activity, in meters per second
- `active_minutes`: Number of minutes of activity. May be different to duration if some of the time was spent e.g. resting.

## commit

A git commit.

- `title`: the commit message
- `hash`
- `url`: Direct link to the commit (optional)
- `author.name`: Commit author name. For example, "John Smith".
- `author.email`
- `repo.name`: Repository name. For example, "timeline".
- `repo.url`: Direct link to the repo (optional)
- `changes.files`: Number of files that changed
- `changes.insertions`: Number of lines inserted
- `changes.deletions`: Number of lines deleted

## file

Describes a file on a filesystem.

- `mixin:file`
- `mixin:preview`
- `mixin:media`
- `mixin:location`: The file's geolocation, if available
- `backup_date`: The date on which a backup created this entry

### file.text

- `decription`: An excerpt from the text file's content

### file.document

### file.image

### file.video

### file.audio

## journal

A journal/diary entry

- `title`: Optional entry title
- `description`: The journal entry, as Markdown.

## message

A message sent by a sender to a recipient. The recipient can be another person or a group.

- `description`: The message body
- `sender_name`: The name of the sender
- `sender_id`: The phone number of the sender
- `recipient_name`: The name of the recipient
- `recipient_id`: The phone number of the recipient
- `mixin:file`: Message attachments
- `mixin:preview`: Preview for the message attachments
- `mixin:media`: Media information about the message attachments

### message.text.sms

### message.facebook

#### message.facebook.audio

#### message.facebook.gif

#### message.facebook.image

#### message.facebook.sticker

#### message.facebook.video

### message.telegram

#### message.telegram.audio

#### message.telegram.gif

#### message.telegram.image

#### message.facebook.file

#### message.telegram.video

## call

An audio or video call.

- `duration`: Call duration, in seconds
- `caller1_name`: Name of the person making the call
- `caller1_id`: ID of the person making the call. In the case of a telephone call, the phone number.
- `caller2_name`: Name of the person or group receiving the call
- `caller2_id`: ID of the person or group receiving the call. In the case of a telephone call, the phone number.

### call.telegram

### call.facebook

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

## location

- `location`
    - `latitude`
    - `longitude`
    - `altitude`: The altitude, in meters
    - `direction`
    - `bearing`
    - `accuracy`: The accuracy, in meters
    - `name`: The name of this location, if available

## previews

- `previews`: A dictionary of different preview sizes. The key is the name of the preview size (for example, "thumbnail"), and the value is the URL of the preview.

## post

- `description`: The post excerpt if it's available, or its full version
- `post_id`: The unique ID of the post
- `post_user`: The author of the post
- `post_thread_id`: The ID of the parent thread
- `post_parent_id`: The unique ID of the parent post (for chained comments)
- `post_body_html`: The longer, HTML version of the post
- `post_score`: The number of likes or upvotes
- `post_url`: The URL of the post. Blank if a permalink can be generated from other entry attributes.
- `post_community`: The sub-community (subreddit, subforum) in which the post was made

## file

- `file`
    - `mimetype`: The file's mimetype. For example "text/markdown"
    - `checksum`: The file's blake2b checksum
    - `path`: The file's absolute path on the filesystem

## media

- `media`
    - `width`: Width in pixels
    - `height`: Height in pixels
    - `orientation`: Orientation in degrees
    - `duration`: Duration in seconds
    - `codec`: Codec used to encode the media
    - `camera`: The camera's make and model.
    - `creation_date`: The date on which the photo was taken. Might differ from the file's modification date.