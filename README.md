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
backup-to-homeserver \
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