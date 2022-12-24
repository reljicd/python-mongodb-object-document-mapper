from mongo_odm.config.config import DBS
from mongo_odm.session.session import MONGO_CLIENT


def delete_mongo_dbs() -> None:
    for db in DBS.keys():
        MONGO_CLIENT.drop_database(db)


def _bootstrapping() -> None:
    delete_mongo_dbs()


_bootstrapping()
