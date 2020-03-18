import os
import sys
import json
import csv
import click
import logging
import requests
from requests.auth import HTTPBasicAuth
from pymongo import MongoClient


def get_collection(collection, logger):
    try:
        client = MongoClient(host=os.environ["DB_SERVER"], port=27017)
        logger.info(f"Opening database connection, server info: {client.server_info()}")
        db = client.get_database("students")
        return db.get_collection(collection)
    except Exception as error:
        logger.error(f"Opening database connection failed: {collection} {error}")
        sys.exit(1)


def insert_student(student, collection, logger):
    try:
        collection.insert_one(student)
    except Exception as error:
        logger.error(f"Inserting student to koski-collection failed: {error}")
        pass


@click.command()
@click.argument("username", type=click.STRING)
@click.argument("password", type=click.STRING)
@click.argument("input_file", type=click.Path(exists=True))
@click.argument("ftype", type=click.STRING)
def main(username, password, input_file, ftype):
    types = {
        "studyrights": "virkailija.opintopolku.fi/koski/api/opiskeluoikeus",
        "studentid": "virkailija.opintopolku.fi/koski/api/oppijanumero",
    }

    logger = logging.getLogger(__name__)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    endpoint = None
    try:
        endpoint = f"https://{types[ftype]}"
    except Exception as error:
        logger.critical(f"Unknown fetch type {ftype}.")
        sys.exit(1)

    logger.info(f"The Koski reader started. Trying to fetch data from url: {endpoint}")

    urls = None
    try:
        with open(input_file, "r", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile, fieldnames=["parameter"], delimiter=";")
            urls = [f"{endpoint}/{str(row['parameter'])}" for row in reader]
        logger.info(f"Getting {len(urls)} parameters to do.")
    except Exception as error:
        logger.error(f"Reading input file failed: {input_file} {error}")
        sys.exit(1)

    collection = get_collection(ftype, logger)
    for url in urls:
        try:
            response = requests.get(
                url, auth=HTTPBasicAuth(str(username), str(password))
            )
            if response.status_code == 200:
                insert_student(response.json(), collection, logger)
            else:
                logger.error(f"Get request failed: {response.status_code} {url}")
        except Exception as error:
            logger.error(f"Get request failed: {url} {error}")


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
