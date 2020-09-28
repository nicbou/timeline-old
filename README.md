# Backup tools

These scripts help me backup data on remote machines, and organize those backups.

## tl;dr

0. Set up SSH keys for `backups@home.nicolasbouliane.com`.
1. Install the scripts as described below.
1. On the source machine, call `backup-to-homeserver [src-dir] [remote-dir]`. It will backup `[src-dir]` to `home.nicolasbouliane.com:/home/backups/[remote-dir]`
2. On the home server, call `incremental-backup /home/backups [dest-dir]`. It will incrementally backup `/home/backups` (all your backups) to `/var/backups/[dest-dir]`.

## Setup

### On the source machine
```
curl --remote-name https://raw.githubusercontent.com/nicbou/backups/master/scripts/backup-to-homeserver -o backup-to-homeserver && chmod a+x backup-to-homeserver && mv backup-to-homeserver /usr/bin/backup-to-homeserver
```

Then you can just call `backup-to-home-server [source-dir] [remote-destination-dir]`.

### On the destination machine
```
curl --remote-name https://raw.githubusercontent.com/nicbou/backups/master/scripts/incremental-backup -o incremental-backup && chmod a+x incremental-backup && mv incremental-backup /usr/bin/incremental-backup
```

Then you can just call `incremental-backup [source-dir] [destination-subdir]`.


## Available scripts

### backup-to-homeserver

**Plain English:** This script backs up different machines to my home server. It copies a local folder to a predefined remote machine. It ignores any files you mention in an `.rsyncignore` file.

**Programmer:** Rsyncs a local source to a hard-coded remote destination (`home.nicolasbouliane.com`). Ignores files listed in `.rsyncignore` files.

**Example:**

```
backup-to-homeserver /home/nicolas home-backup

$ ls /home/nicolas

/home/nicolas
-- hello.txt

$ ls backups@home.nicolasbouliane.com:/home/backups

/home/backups
-- /home-backup
---- hello.txt
```

### incremental-backup

**Plain English:** This script combines backups from other machines, and makes an backup of that. It copies a local folder to another local folder, and keeps a copy of the files that changed since the last backup. It also generates files that describe how the backup went.

**Programmer:** Incrementally backs up a local source to a subdirectory of a hard-coded local destination (`/var/backups`). Metadata about the backup is saved in the destination directory.

**Example:**

```
incremental-backup /home/backups combined-backup

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