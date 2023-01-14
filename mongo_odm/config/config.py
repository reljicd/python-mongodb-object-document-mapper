import importlib
import os
from typing import Dict, List, NamedTuple, Type

import pymongo
import yaml
from reljicd_utils.file_system import files_in_dir

from mongo_odm.config.env_vars import DB_CONFIGS

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

DBS = dict()
for file in files_in_dir(os.path.join(PROJECT_ROOT, DB_CONFIGS),
                         extension='yaml'):
    db_config = yaml.load(open(file, 'r'),
                          Loader=yaml.FullLoader)

    DBS[os.path.basename(file)[:-5]] = db_config


class Field(NamedTuple):
    name: str
    order: int


class Index(NamedTuple):
    fields: List[Field]
    unique: bool = False
    name: str = None


class Collection(NamedTuple):
    db: str
    indices: List[Index]
    model: Type
    mongo_ec2: bool = False


ORDERS = {'asc': pymongo.ASCENDING,
          'desc': pymongo.DESCENDING}


def indices(collection: Dict) -> List[Index]:
    _indices = []
    for index in collection.get('indices', []):
        _fields = []
        for _field in index['fields']:
            if 'order' in index:
                order = ORDERS[index['order']]
            else:
                order = ORDERS['asc']
            _fields.append(Field(name=_field['name'], order=order))
        unique = index.get('unique', False)
        name = index.get('name', None)
        _indices.append(Index(fields=_fields, unique=unique, name=name))

    return _indices


def get_model(_model: str) -> Type:
    model_type = _model.split('.')[-1]
    model_path = _model.rstrip(model_type)[:-1]
    try:
        return getattr(importlib.import_module(model_path), model_type)
    except ModuleNotFoundError:
        return getattr(importlib.import_module('dict_objectify.base.base'),
                       'Base')


def all_collections() -> Dict[str, Collection]:
    _collections = {}
    for db_name, db in DBS.items():
        for collection in db.get('collections', []):
            if 'model' in db:
                model = get_model(db['model'])
            else:
                model = get_model(collection['model'])
            _collections[collection['name']] = Collection(
                db=db_name,
                indices=indices(collection),
                model=model)
    return _collections


COLLECTIONS: Dict[str, Collection] = all_collections()
