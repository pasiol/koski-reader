# koski-reader

The REST client reads student's data from the Koski database and stores data to the MongoDB-database. File aggeregate_vocational.py extracting vocational studies to own collection. Uses docker-compose to run database and scripts.

## Prerequisites

* Docker
* docker-compose

[https://docs.docker.com/engine/install/]

In Mac and Windows use Docker Desktop. 

### Ubuntu

I prefer Canonical maintained packages which are robust.

    sudo apt update && sudo apt install -y docker.io docker-compose
    sudo usermod -aG docker $USER

## Installation

    git clone https://github.com/pasiol/koski-reader.git
    cd koski-reader
    docker-compose build

## Usage

Running the MongoDB database and docker volumes.

    docker-compose up

### Useful commands

    docker ps
    docker volume ls
    docker exec -it database_1 /bin/bash

### Running commands on the reader container

    docker-compose run reader python3 reader.py --help
    Starting koskireader_database_1 ... done
    Usage: reader.py [OPTIONS] USERNAME PASSWORD INPUT_FILE FTYPE

    Options:
    --help  Show this message and exit.

#### Running the Rest-client

You need input file which contains studyrights on the csv-file. It could be generate with the primusquery utility. Put csv input file on the root directory before docker-compose build command. Reader can update old data, so there is no need get always all studyrights only the changed ones. If you remove mongodb docker volume, you also loose all the data. You can import data to host environment with mongoimport and docker-compose commands.

    docker-compose run reader python3 reader.py user password studyrights.csv studyrights

#### Attaching to database container

    docker exec -it koskireader_database_1 /bin/bash
    root@e9cb474b57d5:/# mongo
    > db.disableFreeMonitoring()

    show dbs
    admin   0.000GB
    koski   0.NNNGB
    local   0.000GB
    > use koski
    switched to db koski
    >db.getCollectionNames()
    [ "studyrights" ]
    > db.studyrights.find().count()
    NNNNNN
    > db.studyrights.find().pretty()
    ...
    >exit


    