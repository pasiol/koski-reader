import os
import sys
import json
import csv
import click
import logging
import requests
from requests.auth import HTTPBasicAuth
from pymongo import MongoClient


def get_collection(collection_name, logger):
    try:
        client = MongoClient(host=os.environ["DB_HOST"], port=27017)
        logger.info(f"Opening database connection, server info: {client.server_info()}")
        db = client.get_database("koski")
        collection = db.get_collection(collection_name)
        return collection
    except Exception as error:
        logger.error(f"Opening database connection failed: {collection} {error}")
        sys.exit(1)


def insert_student(student, collection, logger):
    # TODO: transaction
    try:
        result = collection.find({"_id": student["oid"]})
        count_of_documents = len(list(result))
        logger.info(
            f"Trying to find oid: {student['oid']}, result length: {count_of_documents}"
        )
        if count_of_documents > 0:
            try:
                result = collection.delete_many({"_id": student["oid"]})
                logger.info(
                    f"Removing oid: {student['oid']}, count: {result.deleted_count}"
                )
            except Exception as error:
                logger.error(f"Removing oid: {student['oid']}, failed: {error}")
                sys.exit(1)
        result = collection.insert_one(student)
        logger.info(f"Inserting to {collection} oid: {student['oid']}: {result}")
    except Exception as error:
        logger.error(f"Inserting student to {collection}-collection failed: {error}")
        sys.exit(1)


def create_json_file(data, output_path, oid, logger):
    try:
        with open(
            f"{output_path}{os.path.sep}{oid}.json", "w", encoding="utf-8"
        ) as output_file:
            json.dump(data, output_file, sort_keys=True, indent=4)
    except Exception as error:
        logger.error(f"Creating json file {oid}.json failed: {error}")
        sys.exit(1)


def anonymize(response, logger):
    data = None
    try:
        data = dict(response.json())
    except Exception as error:
        logger.info(f"Casting response to JSON failed: {error}")
        sys.exit(1)

    if "henkilö" in data.keys():
        try:
            data["oid"] = data["henkilö"]["oid"]
            data.pop("henkilö", None)
            return data
        except Exception as error:
            logger.info(f"Anonymizing failed: {error}")
            sys.exit(1)
    return data


@click.command()
@click.argument("username", type=click.STRING)
@click.argument("password", type=click.STRING)
@click.argument("input_file", type=click.Path(exists=True))
@click.argument("ftype", type=click.STRING)
def main(username, password, input_file, ftype):
    types = {
        "studyrights": "virkailija.opintopolku.fi/koski/api/opiskeluoikeus",
        "studentid": "virkailija.opintopolku.fi/koski/api/oppija",
    }

    logger = logging.getLogger(__name__)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    collection = None
    endpoint = None
    try:
        endpoint = f"https://{types[ftype]}"
    except Exception as error:
        logger.critical(f"Unknown fetch type {ftype}.")
        sys.exit(1)

    logger.info(f"The Koski reader started. Trying to fetch data from url: {endpoint}")

    urls = None
    try:
        with open(input_file, "r", encoding="utf-8-sig") as csvfile:
            reader = csv.DictReader(csvfile, fieldnames=["parameter"], delimiter=";")
            urls = [f"{endpoint}/{str(row['parameter'])}" for row in reader]
        logger.info(f"Getting {len(urls)} parameters to do.")
    except Exception as error:
        logger.error(f"Reading input file failed: {input_file} {error}")
        sys.exit(1)
    if output_path == "":
        collection = get_collection(ftype, logger)
    for url in urls:
        oid = url.split("/")[-1]
        logger.info(f"Processing id: {oid}")
        try:
            response = requests.get(
                url, auth=HTTPBasicAuth(str(username), str(password))
            )
            if response.status_code == 200:
                data = anonymize(response, logger)
                data["_id"] = oid
                if output_path == "":
                    insert_student(data, collection, logger)
                else:
                    create_json_file(data, output_path, oid, logger)
            else:
                logger.error(f"Get request failed: {response.status_code} {url}")
        except Exception as error:
            logger.error(f"Get request failed: {url} {error}")


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
