import os
import re
import sys
import json
import csv
import click
import logging
import pandas as pd
from difflib import SequenceMatcher
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


def try_to_find_almost_matching_name(oid, name, accepted_ratio, collection, logger):
    try:
        for accomplishment in collection.find({"oid": oid}):
            s = SequenceMatcher(None, accomplishment["nimi"], name)
            if s.ratio() >= float(accepted_ratio):
                return True
    except Exception as error:
        logger.error(
            f"Trying to find almost matching name failed: {collection} {error}"
        )
        pass
    return False


@click.command()
@click.argument("match_ratio", type=click.FLOAT)
@click.option("-o", "output_path", type=click.Path(exists=True))
def main(match_ratio, output_path):

    logger = logging.getLogger(__name__)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    koski_vocational_collection = get_collection(
        "reports", "koski_vocational_accomplishments", logger
    )
    koski_vocational_accomplishments = pd.DataFrame(
        list(koski_vocational_collection.find({}))
    )

    primus_vocational_collection = get_collection(
        "reports", "primus_vocational_accomplishments", logger
    )
    primus_vocational_accomplishments = pd.DataFrame(
        list(primus_vocational_collection.find({}))
    )

    outer_primus_with_name = pd.merge(
        primus_vocational_accomplishments,
        koski_vocational_accomplishments,
        how="outer",
        on=["oid", "nimi"],
    )
    outer_primus_with_name.info()
    filter = outer_primus_with_name["_id_y"].isnull()
    missing_accomplishments_with_name = outer_primus_with_name[filter].loc[
        :, ["oid", "nimi", "päivämäärä"]
    ]
    columns = ["opiskeluoikeuden tunniste", "suorituksen nimi", "pvm"]
    df = pd.DataFrame(columns=columns)
    for missing_accomplishment in missing_accomplishments_with_name.iterrows():
        oid = missing_accomplishment[1].values[0]
        name = missing_accomplishment[1].values[1]
        date = {missing_accomplishment[1].values[2]}
        found = try_to_find_almost_matching_name(
            oid, name, match_ratio, koski_vocational_collection, logger
        )
        if not found:
            print(
                f"{missing_accomplishment[1].values[0]};{missing_accomplishment[1].values[1]};"
            )
            df = df.append(pd.DataFrame([[oid, name, date]], columns=columns))
        else:
            logger.info(f"Founded almost matching name for name {name}.")

    if output_path is not None:
        df.to_csv(
            f"{output_path}{os.path.sep}missing_from_koski_vocational_with_name.csv",
            sep=";",
            index=False,
            encoding="windows-1252",
        )
    outer_primus_with_name.info()


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
