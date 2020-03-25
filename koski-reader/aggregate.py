import os
import sys
import json
import csv
import click
import logging
from pymongo import MongoClient


def get_collection(db, collection_name, logger):
    try:
        client = MongoClient(host=os.environ["DB_HOST"], port=27017)
        logger.info(f"Opening database connection, server info: {client.server_info()}")
        db = client.get_database(db)
        collection = db.get_collection(collection_name)

        return collection
    except Exception as error:
        logger.error(f"Opening database connection failed: {collection} {error}")
        sys.exit(1)


def project_primus_accomplishments(collection, logger):
    pipeline = [
        {
            "$project": {
                "_id": 0,
                "oid": "opiskeluoikeuden tunniste",
                "nimi": "suorituksen nimi",
                "laajuus": "suorituksen laajuus",
                "arvosana": "koski-arvosana",
                "tutkinnon osan koodi": 1,
                "koski-tunniste": 1,
            }
        },
        {"$merge": {"into": {"db": "reports", "coll": "primus_accomplishments"}}},
    ]

    try:
        collection.aggregate(pipeline)
        logger.info(f"Executing aggregate pipeline succeed: {collection}")
        return None
    except Exception as error:
        logger.error(f"Executing aggregate pipeline failed: {collection} {error}")
        sys.exit(1)


def unwind_koski_accomplishments(collection, logger):

    pipeline = [
        {
            "$project": {
                "_id": 0,
                "suoritukset": {"$arrayElemAt": ["$suoritukset", 0]},
                "oid": 1,
            }
        },
        {"$unwind": "$suoritukset.osasuoritukset"},
        {
            "$project": {
                "oid": 1,
                "koodi": "$suoritukset.osasuoritukset.koulutusmoduuli.tunniste.koodiarvo",
                "nimi": "$suoritukset.osasuoritukset.koulutusmoduuli.tunniste.nimi.fi",
                "tutkinnonosanryhmä": "$suoritukset.osasuoritukset.tutkinnonOsanRyhmä.nimi.fi",
                "laajuus": "$suoritukset.osasuoritukset.koulutusmoduuli.laajuus.arvo",
                "yksikkö": "$suoritukset.osasuoritukset.koulutusmoduuli.laajuus.yksikkö.nimi.fi",
                "rahoituksenpiirissä": "$suoritukset.osasuoritukset.tunnustettu.rahoituksenPiirissä",
                "arvosana": {
                    "$arrayElemAt": ["$suoritukset.osasuoritukset.arviointi", 0]
                },
            }
        },
        {
            "$project": {
                "oid": 1,
                "koodi": 1,
                "nimi": 1,
                "tutkinnonOsanRyhmä": 1,
                "laajuus": 1,
                "yksikkö": 1,
                "arvosana": "$arvosana.arvosana.koodiarvo",
                "hyväksytty": "$arvosana.hyväksytty",
            }
        },
        {"$merge": {"into": {"db": "reports", "coll": "koski_accomplishments"}}},
    ]

    try:
        collection.aggregate(pipeline)
        logger.info(f"Executing aggregate pipeline succeed: {collection}")
        return None
    except Exception as error:
        logger.error(f"Executing aggregate pipeline failed: {collection} {error}")
        sys.exit(1)


def merge_accomplishments():
    pipeline = []


@click.command()
@click.argument("output_path", type=click.Path(exists=True))
def main(output_path):

    logger = logging.getLogger(__name__)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    koski_studyrights = get_collection("koski", "studyrights", logger)
    unwind_koski_accomplishments(koski_studyrights, logger)
    primus_accomplishments = get_collection("primus", "studyrights", logger)
    project_primus_accomplishments(primus_accomplishments, "accomplishments", logger)


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
