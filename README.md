# koski-reader

The REST client reads student's data from the Koski database and stores data to the MongoDB-database. File aggeregate_vocational.py extracting vocational studies to own collection. Uses docker-compose to run database and scripts.

## Prerequisites

* Docker
* docker-compose

### Ubuntu

    apt update && apt install -y docker.io docker-compose

## Usage

Install docker and docker-compose 

    git clone https://github.com/pasiol/koski-reader.git
    cd koski-reader

    docker-compose pull && docker-compose build
    docker-compose up

### Running Rest-client

    