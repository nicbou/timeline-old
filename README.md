# Backup tools

These scripts help me backup data between different servers.

### Available scripts

#### backup

**Plain English:** This script backs up different machines to my home server. It copies a local folder to a predefined remote machine. It ignores any files you mention in an `.rsyncignore` file.

**Programmer:** Rsyncs a local source to a hard-coded remote destination. Ignores files listed in `.rsyncignore` files.

**Example:**

```
backup /home/nicolas home-backup

$ ls /home/nicolas

/home/nicolas
-- hello.txt

$ ls backups@home.nicolasbouliane.com:/home/backups

/home/backups
-- /home-backup
---- hello.txt
```

#### incremental-backup

**Plain English:** This script combines backups from other machines, and makes an backup of that. It copies a local folder to another local folder, and keeps a copy of the files that changed since the last backup. It also generates files that describe how the backup went.

**Programmer:** Incrementally backs up a local source to a subdirectory of a hard-coded local destination. Metadata about the backup is saved in the destination directory.

**Example:**

```
incremental-backup /home/nicolas home-backup

$ ls /home/nicolas

/home/nicolas
-- hello.txt

$ ls /var/backups

/var/backups
-- /home-backup
---- /2020-09-28 17:45
------ /files
-------- hello.txt
```
