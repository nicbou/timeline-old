# Backup tools

These scripts help me backup data on remote machines, and organize those backups.

I use rsync to copy the files. It only transfers the files that changed, saving time and bandwidth.

## Setup

### On the source machine
```
curl --remote-name https://raw.githubusercontent.com/nicbou/backups/master/scripts/backup-to-remote -o backup-to-remote && chmod a+x backup-to-remote && mv backup-to-remote /usr/local/bin/backup-to-remote
```

You will also need to [copy SSH keys](https://www.digitalocean.com/community/tutorials/how-to-set-up-ssh-keys-2) so that rsync works without asking for a password.

```
ssh-copy-id user@remote-host
```

### On the destination machine
```
curl --remote-name https://raw.githubusercontent.com/nicbou/backups/master/scripts/incremental-backup -o incremental-backup && chmod a+x incremental-backup && mv incremental-backup /usr/local/bin/incremental-backup
```

## Usage

### backup-to-remote

**Plain English:** This script copies a local folder to another machine. It ignores any files you mention in an `.rsyncignore` file.

**Programmer:** Rsyncs a local source to a subdirectory on a remote destination. Ignores files listed in `.rsyncignore` files.

**Example:**

```
$ backup-to-homeserver \
    -u nicolas \
    -H home.nicolasbouliane.com \
    -p 2222 \
    -o rsync-log.txt \
    /local/files \
    backups/files-backup

$ ls /local/files

/local/files
-- hello.txt

$ ls nicolas@home.nicolasbouliane.com:/home/nicolas/backups/files-backup

/home/nicolas/backups
-- /home-backup
---- hello.txt
```

### incremental-backup

**Plain English:** This script combines backups from other machines, and makes an backup of that. It copies a local folder to another local folder, and keeps a copy of the files that changed since the last backup. It also generates files that describe how the backup went.

**Programmer:** Incrementally backs up a local source to a subdirectory of a hard-coded local destination (`/var/backups`). Metadata about the backup is saved in the destination directory.

**Example:**

```
$ incremental-backup /home/backups combined-backup

$ ls /home/backups

/home/backups
-- hello.txt

$ ls /var/backups

/var/backups
-- /combined-backup
---- /2020-09-28 17:45
------ /files
-------- hello.txt
---- /latest -> /2020-09-28 17:45
```

### generate-history

**Plain English:** Generates a list of files in a directory, in JSON format. The list groups files by modification date, and contains useful information about each file. Each file entry has a schema. The schema says what kind of file it is, and what kind of information is in the entry.

**Programmer:** Returns a JSON list of files to be consumed by a frontend application. File entries are grouped by date, and contain useful file metadata. File entries have a schema that describe the file type, and dictate what attributes this entry has.

**Example:**

```

$ generate-history ~/Documents output.json

$ cat output.json

{
   "dateRange":[
      "2009-03-15",
      "2020-10-01"
   ],
   "dateGenerated":"2020-10-02T11:19",
   "entries":{
      "2020-10-01":[
         {
            "schema":"file.code.css",
            "title":"style.css",
            "description":"",
            "dateUpdated":"2020-10-01T11:00",
            "path":"/Users/nicolas/Documents/Projects/AllAboutBerlin/source/site/craft/templates/css/style.css",
            "checksum":"b0ce67831a9b8379db6b79cbe2ec94b4500f80fd6f7e013a830cf7ba663e413f3e466ed5417f558d48d6760d13e7fe2af07c7ad59a25cadde7bd7c681726023d"
         }
      ],
      "2020-09-30":[
         {
            "schema":"file.code.css",
            "title":"style.css",
            "description":"",
            "dateUpdated":"2020-09-30T18:43:02",
            "path":"/Users/nicolas/Documents/Projects/NicolasBouliane3/source/site/static/css/style.css",
            "checksum":"f4dafad10572b264ceed6b61fcf761def42cfbb8b203bf5e2dd1928a1b829ca101ea2c548e30c38b81e4b4a1b4679df4a3d561e77829e21b4ac0f4b208b16e9c"
         },
         {
            "schema":"file.code.javascript",
            "title":"events.js",
            "description":"",
            "dateUpdated":"2020-09-30T18:40:52",
            "path":"/Users/nicolas/Documents/Projects/NicolasBouliane3/source/site/static/js/events.js",
            "checksum":"a2f8ed83a574eb91f8981ac45b773feae17b72949a908bf7955e355926ea61241346d8af7747027cc164d6e838426b073089bbb9be2c5acf5db4c5e4bd0cd1c0"
         }
      ],
...
```

### generate-previews

**Plain English:** Generates file previews for file histories created by `generate-history`. Existing previews are reused. Obsolete previews are deleted. The previews are named after the file's checksum.

**Example:**

```
$ generate-previews output.json previews

$ ls previews

a2f8ed83a574eb91f8981ac45b773feae17b72949a908bf7955e355926ea61241346d8af7747027cc164d6e838426b073089bbb9be2c5acf5db4c5e4bd0cd1c0.jpg
f4dafad10572b264ceed6b61fcf761def42cfbb8b203bf5e2dd1928a1b829ca101ea2c548e30c38b81e4b4a1b4679df4a3d561e77829e21b4ac0f4b208b16e9c.mp3
...
```