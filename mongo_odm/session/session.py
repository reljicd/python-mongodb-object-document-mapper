from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from mongo_odm.config.config import COLLECTIONS
from mongo_odm.config.env_vars import (MONGO_CERT_PATH, MONGO_HOST,
                                       MONGO_PASSWORD,
                                       MONGO_PORT, MONGO_USERNAME,
                                       MONGO_USE_REPLICA_SET, MONGO_USE_SSL)

MONGO_PARAMS = {'host': MONGO_HOST,
                'port': MONGO_PORT,
                'maxPoolSize': 5000,
                'retryWrites': False}

if MONGO_USERNAME:
    MONGO_PARAMS['username'] = MONGO_USERNAME
    MONGO_PARAMS['password'] = MONGO_PASSWORD
    MONGO_PARAMS['authSource'] = 'admin'
    MONGO_PARAMS['authMechanism'] = 'SCRAM-SHA-1'
if MONGO_USE_SSL:
    MONGO_PARAMS['ssl'] = MONGO_USE_SSL
    MONGO_PARAMS['ssl_ca_certs'] = MONGO_CERT_PATH
if MONGO_USE_REPLICA_SET:
    MONGO_PARAMS['replicaSet'] = 'rs0'
    MONGO_PARAMS['readPreference'] = 'secondaryPreferred'

MONGO_CLIENT = MongoClient(**MONGO_PARAMS)


def db(name: str) -> Database:
    return MONGO_CLIENT[name]


def collection(_collection: str) -> Collection:
    _coll = COLLECTIONS[_collection]
    _db = db(name=_coll.db)
    if _collection not in _db.list_collection_names():
        create_collection(_collection)
    return _db[_collection]


def create_collection(_collection: str) -> None:
    _coll = COLLECTIONS[_collection]
    _db = db(name=_coll.db)
    _db.create_collection(_collection)
    create_indices(_collection)


def create_indices(_collection: str) -> None:
    _coll = COLLECTIONS[_collection]
    _db = db(name=_coll.db)
    _indices = _coll.indices
    if _indices:
        coll = _db[_collection]
        for index in _indices:
            if index.name:
                coll.create_index(index.fields,
                                  unique=index.unique,
                                  name=index.name)
            else:
                coll.create_index(index.fields,
                                  unique=index.unique)
