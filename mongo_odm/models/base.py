import datetime
from typing import Dict

from dict_objectify import Base, Datetime, Text, dict_base_hash

NON_HASHABLE_FIELDS = ['_id', 'updated_at', 'created_at', '_hash', '_metadata']


class MongoBase(Base):
    _id = Text()
    _hash = Text()
    created_at = Datetime()
    updated_at = Datetime()

    def __init__(self, data_dict: Dict = None, **kwargs) -> None:
        super().__init__(data_dict=data_dict, **kwargs)
        if not data_dict:
            super().__setattr__('created_at', now())
            super().__setattr__('updated_at', now())
        self.check_hash_and_update()

    def __hash__(self):
        dct = self.data_dict.copy()
        for field in NON_HASHABLE_FIELDS:
            if field in dct:
                del dct[field]
        return dict_base_hash(dct)

    def check_hash_and_update(self):
        _hash = str(self.__hash__())
        if not hasattr(self, '_hash') or _hash != self._hash:
            super().__setattr__('updated_at', now())
            super().__setattr__('_hash', _hash)


def now() -> datetime:
    return datetime.datetime.now()
