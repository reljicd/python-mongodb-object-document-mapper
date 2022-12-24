from typing import List

from mongo_odm.config.config import COLLECTIONS
from mongo_odm.repos.repo import MongoRepo


class MongoRepos(object):
    _cache = {}

    @classmethod
    def all_repos(cls) -> List[MongoRepo]:
        return [cls.repo(name)
                for name in COLLECTIONS.keys()]

    @classmethod
    def repo(cls, name: str) -> MongoRepo:
        if name not in cls._cache:
            _repo = MongoRepo(name)
            cls._cache[name] = _repo

        return cls._cache[name]
