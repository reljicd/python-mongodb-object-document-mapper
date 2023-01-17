import multiprocessing
from dataclasses import dataclass
from multiprocessing import Process, Queue
from typing import (Dict, Generator, Iterator, List, NamedTuple, Optional,
                    Tuple, Type, TypeVar, Union)

from dict_objectify import Base
from pymongo import UpdateOne
from pymongo.errors import DuplicateKeyError
from pymongo.operations import InsertOne
from pymongo.results import BulkWriteResult, DeleteResult

from mongo_odm.config.config import COLLECTIONS
from mongo_odm.session.session import collection, db
from mongo_odm.utils.utils import chunks, iter_counter, spawn_scope

BaseType = TypeVar('BaseType', bound=Base)


class Range(NamedTuple):
    skip: int
    limit: int


@dataclass
class SortLimit:
    sort_field: str
    sort_direction: int
    limit: int
    skip: int = 0


@dataclass
class Projection:
    fields_to_skip: List[str] = None
    fields_to_include: List[str] = None
    skip_id_field: bool = False

    def projection(self) -> Dict:
        projection = dict()

        if self.fields_to_skip:
            projection.update({field_to_skip: False
                               for field_to_skip in self.fields_to_skip})
        if self.fields_to_include:
            projection.update({field_to_include: True
                               for field_to_include in self.fields_to_include})
        if self.skip_id_field:
            projection['_id'] = False

        return projection


class MongoDocRepo(object):
    """ This is the most basic Mongo interface that deals with dictionaries
        directly. """

    def __init__(self,
                 _collection: str,
                 _db: str = None) -> None:
        if _collection in COLLECTIONS:
            self._collection = collection(_collection)
        else:
            self._collection = db(_db)[_collection]

    def all(self,
            projection: Union[Projection, Dict[str, bool], List[str]] = None,
            print_progress: bool = False,
            print_step: int = 1000) -> Generator[Dict, None, None]:
        yield from self.find(query_filter={},
                             projection=projection,
                             print_progress=print_progress,
                             print_step=print_step)

    def all_parallel(self,
                     projection: Union[Dict[str, bool], List[str]] = None,
                     print_progress: bool = False,
                     print_step: int = 10000) -> Generator[Dict, None, None]:
        _query = self._all_parallel(projection)
        if print_progress:
            _query = iter_counter(_query,
                                  print_step=print_step)
        yield from _query

    def _all_parallel(self,
                      projection: Union[Dict[str, bool], List[str]] = None
                      ) -> Generator[Dict, None, None]:
        total = self.count()

        half_count = total // 2
        other_half_count = total - half_count

        sorts_limits = [SortLimit(sort_field='updated_at',
                                  sort_direction=1,
                                  limit=half_count),
                        SortLimit(sort_field='updated_at',
                                  sort_direction=-1,
                                  limit=other_half_count)
                        ]

        num_of_processes = len(sorts_limits)

        with spawn_scope():
            queue = Queue(maxsize=100)
            processes = []

            for sort_limit in sorts_limits:
                p = Process(
                    target=self._find_parallel,
                    args=(queue,
                          self._collection.name,
                          {},
                          projection,
                          sort_limit.limit,
                          sort_limit.skip,
                          [(sort_limit.sort_field, sort_limit.sort_direction)]),
                )
                p.start()
                processes.append(p)

            workers_done = 0
            while workers_done != num_of_processes:
                chunk = queue.get()
                if chunk != 'DONE':
                    yield from chunk
                else:
                    workers_done += 1

            for process in processes:
                process.terminate()

    @staticmethod
    def _find_parallel(queue: Queue,
                       _collection: str,
                       query_filter: Dict = None,
                       projection: Union[Dict[str, bool], List[str]] = None,
                       limit: int = 0,
                       skip: int = 0,
                       sort: List[Tuple] = None):
        from mongo_odm.repos.repos import MongoRepos

        _query = MongoRepos.repo(_collection).find(query_filter=query_filter,
                                                   projection=projection,
                                                   limit=limit,
                                                   skip=skip,
                                                   sort=sort)
        for chunk in chunks(_query, n=1000):
            queue.put(list(chunk))

        queue.put('DONE')

    def find(self,
             query_filter: Dict = None,
             limit: int = 0,
             max_time_ms: Optional[int] = None,
             skip: int = 0,
             sort: List[Tuple] = None,
             projection: Union[Projection, Dict[str, bool], List[str]] = None,
             batch_size: int = 100,
             print_progress: bool = False,
             print_step: int = 1000) -> Generator[Dict, None, None]:
        if projection and isinstance(projection, Projection):
            projection = projection.projection()

        _query = self._collection.find(filter=query_filter,
                                       limit=limit,
                                       skip=skip,
                                       sort=sort,
                                       projection=projection,
                                       batch_size=batch_size,
                                       max_time_ms=max_time_ms)

        count = self._collection.count_documents(
            filter=query_filter,
            limit=limit,
            skip=skip,
            max_time_ms=max_time_ms) if print_progress else None

        if print_progress:
            _query = iter_counter(
                iterable=_query,
                total=count,
                print_step=print_step,
                print_message=f'Working on')

        yield from _query

    def aggregate(self,
                  pipeline: List[Dict],
                  batch_size: int = 100) -> Generator[Dict, None, None]:

        _aggregate = self._collection.aggregate(pipeline,
                                                batchSize=batch_size)

        yield from _aggregate

    def find_one(self, query_filter: Dict) -> Optional[Dict]:
        return self._collection.find_one(query_filter)

    def update_one(self, _id: str, update: Dict, upsert: bool = False) -> None:
        self._collection.update_one(
            {'_id': _id}, {'$set': update}, upsert=upsert)

    def insert_one(self, doc: Dict) -> None:
        self._collection.insert_one(doc)

    def replace_one(self, doc: Dict) -> None:
        self._collection.replace_one(filter={'_id': doc['_id']},
                                     replacement=doc)

    def insert_or_replace_one(self, doc: Dict) -> None:
        try:
            self.insert_one(doc)
        except DuplicateKeyError:
            self.replace_one(doc)

    def bulk_insert(self,
                    docs: Iterator[Dict]) -> Optional[BulkWriteResult]:
        requests = [InsertOne(doc) for doc in docs]
        if requests:
            return self._collection.bulk_write(requests, ordered=False)

    def bulk_update(self,
                    docs: Iterator[Dict]) -> Optional[BulkWriteResult]:
        requests = []
        for doc in docs:
            requests.append(UpdateOne({'_id': doc['_id']},
                                      {'$set': doc},
                                      upsert=True))
        if requests:
            return self._collection.bulk_write(requests, ordered=False)

    def delete_all(self, query_filter: Dict = None) -> None:
        if not query_filter:
            query_filter = {}
        self._collection.delete_many(query_filter)

    def delete_one(self, query_filter: Dict) -> DeleteResult:
        return self._collection.delete_one(query_filter)

    def delete_by_id(self, _id: str) -> DeleteResult:
        return self.delete_one({'_id': _id})

    def exists(self, query_filter: Dict) -> bool:
        return bool(self.count(query_filter))

    def exists_one(self, query_filter: Dict) -> bool:
        return self.count(query_filter) == 1

    def exists_id(self, _id: str) -> bool:
        return self.exists_one({'_id': _id})

    def distinct(self, key: str, query_filter: Dict) -> List[str]:
        return list(self._collection.distinct(key, query_filter))

    def count(self, query_filter: Dict = None) -> int:
        if query_filter is None:
            query_filter = {}
        return self._collection.count_documents(query_filter)

    def field_values(self,
                     field_name: str,
                     query_filter: Dict = None,
                     batch_size: int = 100,
                     print_progress: bool = False,
                     print_step: int = 1000) -> Generator:
        projection = {field_name: True}
        if field_name is not '_id':
            projection['_id'] = False
        return (doc[field_name] for doc
                in self.find(query_filter,
                             projection=projection,
                             batch_size=batch_size,
                             print_progress=print_progress,
                             print_step=print_step))

    def count_distinct_field_values(self, field: str) -> Optional[int]:
        pipeline = [
            {'$group': {'_id': f'${field}'}},
            {'$group': {'_id': 1, 'count': {'$sum': 1}}},
        ]
        try:
            cursor = self._collection.aggregate(pipeline)
            distinct_target_field = list(cursor)[0]['count']

            return distinct_target_field

        except IndexError:
            return None

    def all_ids(self,
                limit: int = 0,
                skip: int = 0,
                batch_size: int = 100,
                print_progress: bool = False,
                print_step: int = 1000) -> Generator[str, None, None]:
        _query = self.find(query_filter={},
                           projection={'_id': True},
                           limit=limit,
                           skip=skip,
                           batch_size=batch_size,
                           print_progress=print_progress,
                           print_step=print_step)
        all_ids = (doc['_id'] for doc in _query)
        yield from all_ids

    def all_ids_chunks(
            self,
            limit: int = 0,
            skip: int = 0,
            batch_size: int = 100,
            print_progress: bool = False,
            print_step: int = 1000) -> Generator[List[str], None, None]:
        yield from (list(chunk) for chunk in
                    chunks(self.all_ids(limit=limit,
                                        skip=skip,
                                        batch_size=batch_size,
                                        print_progress=print_progress,
                                        print_step=print_step),
                           n=batch_size))


class MongoObjRepo(MongoDocRepo):
    """ This Mongo interface uses our Base models, but does not require the
        additional restrictions of a Pipeline Model.
        It distinguishes its methods from the parent class by using
        `_obj` or `_objs` in the method name."""

    def __init__(self,
                 _collection: str,
                 _db: str = None,
                 _type: Type = BaseType) -> None:
        super().__init__(_collection, _db)
        self._type = _type

    def all_objs(self,
                 num_of_processes: int = 1,
                 print_progress: bool = False,
                 print_step: int = 1000) -> Generator[BaseType, None, None]:
        yield from self.query({},
                              num_of_processes=num_of_processes,
                              print_progress=print_progress,
                              print_step=print_step)

    def insert_obj(self, doc: BaseType) -> None:
        self.insert_one(doc.data_dict)

    def delete_obj(self, doc: BaseType) -> None:
        self.delete_by_id(doc._id)

    def replace_obj(self, doc: BaseType) -> None:
        self._collection.replace_one(filter={'_id': doc._id},
                                     replacement=doc.data_dict)

    def insert_or_replace_obj(self, doc: BaseType) -> None:
        try:
            self.insert_obj(doc)
        except DuplicateKeyError:
            self.replace_obj(doc)

    def query_by_id(self, _id: str) -> Optional[BaseType]:
        return self.query_one({'_id': _id})

    def query_one(self, query_filter: Dict) -> Optional[BaseType]:
        json_dict = self.find_one(query_filter)
        if json_dict:
            return self._type(json_dict)

    def query_aggregate(
            self,
            pipeline: List[Dict],
            num_of_processes: int = 1,
            batch_size: int = 100) -> Generator[BaseType, None, None]:
        _query = self.aggregate(pipeline,
                                batch_size=batch_size)

        yield from self._models_from_json_dicts(
            json_dicts=_query,
            num_of_processes=num_of_processes)

    def query(self,
              query_filter: Dict = None,
              limit: int = 0,
              max_time_ms: Optional[int] = None,
              skip: int = 0,
              sort: List[Tuple] = None,
              projection: Union[Dict[str, bool], List[str]] = None,
              batch_size: int = 100,
              num_of_processes: int = 1,
              print_progress: bool = False,
              print_step: int = 1000) -> Generator[BaseType, None, None]:
        _query = self.find(query_filter=query_filter,
                           limit=limit,
                           max_time_ms=max_time_ms,
                           skip=skip,
                           sort=sort,
                           projection=projection,
                           batch_size=batch_size,
                           print_progress=print_progress,
                           print_step=print_step)

        yield from self._models_from_json_dicts(
            json_dicts=_query,
            num_of_processes=num_of_processes)

    def _models_from_json_dicts(
            self,
            json_dicts: Iterator[Dict],
            num_of_processes: int = 1) -> Generator[BaseType, None, None]:

        if num_of_processes == 1:
            yield from map(self._type, json_dicts)
        else:
            with multiprocessing.Pool(processes=num_of_processes) as p:
                for json_dict_chunk in chunks(json_dicts, 100000):
                    yield from p.imap_unordered(self._type,
                                                json_dict_chunk,
                                                1000)


class MongoRepo(MongoObjRepo):
    def __init__(self, _collection: str) -> None:
        super().__init__(_db=COLLECTIONS[_collection].db,
                         _collection=_collection,
                         _type=COLLECTIONS[_collection].model)
