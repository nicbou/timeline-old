# Personal timeline - Development

This document provides assistance in setting up and debugging during the development process for this repo. Everything presented is merely a suggestion to make the process easier when unsure.

## Development

If you would like to edit the source code and make changes then this section contains suggested information to help. 

Many possible debugging environments are available. However, this document uses Visual Studio Code (VSc), in part due to its prevelance as a text editor with extentions. You will need:

 * Visual Studio Code (Official Closed-Source Version)
 * Extentions:
   * Python  (`ms-python.python`)
   * [Remote - Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) (`ms-vscode-remote.remote-containers`)
   * [Docker](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-docker) (`ms-azuretools.vscode-docker`)

This provides a set up that allows managing docker containers, as well as attaching to them and remotely debugging them.

Make use of the `docker-compose.dev.yml` file which contains additional tools for development and debugging, such as [pgAdmin](https://www.pgadmin.org/). An example way to use this is to edit the `.env` file `COMPOSE_FILE=docker-compose.yml:docker-compose.dev.yml`

### Browse the database

Use pgAdmin in the dev compose file. Access if by default at http://localhost:5050 with credentials provided in the dev compose file (`PGADMIN_DEFAULT_EMAIL` `PGADMIN_DEFAULT_PASSWORD`). Add a server with the name of the service (default is `timeline-db`), and the `POSTGRES_USER` and `POSTGRES_PASSWORD` from `docker-compose.yml` as the database username and password respectively.

### Developing Backend/Django 

If using VSc, navigate to the `Remote Explorer` side-tab, which is added by the `Remote- Containers` extention. Find the `timeline-backend` container under `Dev Containers` and click `Attach to container`. This will open a new VSc window in the `backend` container. Commands ran from this window will be exquivalent to running `docker exec backend $` on the command line, i.e. running commands within the container. 

#### Debug import/export process

A default debug launch configuration is provided, called `Django Backend: Import`. This executes the command `python manage.py import`, which triggers the import process for sources and archives. This launch configuration is useful for developing new sources and archives.

**Note** If developing or debugging sources and archives, it is recommended to disable the automatic cron jobs (i.e. comment out the line 

``` bash 
0 * * * * /usr/src/app/cron-tasks.sh
```

from `backend/crontab`). This is to ensure the import process is only triggered manually when desired.

#### Debug Backend Server

A debug launch called `Django Debug Server` is provided, which launches a testing server available for access from a web terminal in the local host. This option is useful to debug API calls which can be made from the web interface for this container (a popup in VSc should tell how to access it). It is useful to create and check API calls, but is not connected to the frontend or other containers, so cannot be used to debug frontend API calls.

## Adding a new data input

This section covers how to add new data streams. Possible data streams are separated into two categories:
 1. Archives. Which are files and folders uploaded by the user. They do not change unless manaually managed. 
 2. Sources. Access the data via API to external sites, updated often with new data or changing previous data.

### Archives

### Sources

Create a new python file in `backend/source/backup/models/`. Define the model class, and it should inherit from `BaseSource` usually, or `OAuthSource` if it requires OAuth access for the data.

Create a `process` function that handles the creation of timeline "events" that should be considered individual events that can be displayed on the timeline.