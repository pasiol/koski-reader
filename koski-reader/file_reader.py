import os
import sys
import json
import csv
import click
import logging
from pymongo import MongoClient


def get_collection(collection_name, logger):
    try:
        client = MongoClient(host=os.environ["DB_HOST"], port=27017)
        logger.info(f"Opening database connection, server info: {client.server_info()}")
        db = client.get_database("primus")
        collection = db.get_collection(collection_name)
        collection.delete_many({})
        return collection
    except Exception as error:
        logger.error(f"Opening database connection failed: {collection} {error}")
        sys.exit(1)


def insert_student(student, collection, logger):
    try:
        result = collection.insert_one(student)
        logger.info(f"Inserting to {collection} : {result}")
    except Exception as error:
        logger.error(f"Inserting student to {collection}-collection failed: {error}")
        pass


@click.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option("-e", "encoding", default="utf-8-sig")
def main(input_file, encoding):

    logger = logging.getLogger(__name__)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    primus_accomplishments = None

    try:
        with open(input_file, "r", encoding=encoding) as input_file:
            reader = csv.DictReader(input_file, delimiter=";")
            primus_accomplishments = [row for row in reader]
    except Exception as error:
        logger.error(f"Reading input file failed: {input_file} {error}")
        sys.exit(1)

    collection = get_collection("accomplishments", logger)
    for accomplishment in primus_accomplishments:
        insert_student(accomplishment, collection, logger)


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
