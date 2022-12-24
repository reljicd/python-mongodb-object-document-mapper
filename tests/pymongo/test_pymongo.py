import pytest
from pymongo import MongoClient
from pymongo.collection import Collection

from mongo_odm.config.env_vars import MONGO_HOST, MONGO_PORT

MONGO_DB = 'test'
POST = {'_id': 1,
        'author': 'Mike',
        'text': 'My first blog post!',
        'tags': ['mongodb', 'python', 'pymongo']}


@pytest.fixture(scope='module')
def mongo_collection() -> Collection:
    client = MongoClient(MONGO_HOST, MONGO_PORT)
    db = client[MONGO_DB]
    return db.posts


@pytest.fixture()
def empty_collection(mongo_collection: Collection) -> None:
    """ Resets Collection before each test to initial testing state """
    mongo_collection.delete_many({})


def test_create_one(mongo_collection: Collection,
                    empty_collection: None) -> None:
    post_id = mongo_collection.insert_one(POST).inserted_id
    assert post_id == POST['_id']


def test_update(mongo_collection: Collection,
                empty_collection: None) -> None:
    test_create_one(mongo_collection, empty_collection)
    new_name = 'John'
    mongo_collection.update_one({'_id': POST['_id']},
                                {'$set': {'author': new_name}})
    updated_post = mongo_collection.find_one({'_id': POST['_id']})
    assert updated_post['author'] == new_name


def test_insert_with_update(mongo_collection: Collection,
                            empty_collection: None) -> None:
    mongo_collection.update_one({'_id': POST['_id']}, {'$set': POST},
                                upsert=True)
    inserted_post = mongo_collection.find_one({'_id': POST['_id']})
    assert inserted_post == POST

    # Try inserting one more time, and making sure we inserted it only once
    mongo_collection.update_one({'_id': POST['_id']}, {'$set': POST},
                                upsert=True)
    count_documents = mongo_collection.count_documents({'_id': POST['_id']})
    assert count_documents == 1


def test_find_one(mongo_collection: Collection,
                  empty_collection: None) -> None:
    test_create_one(mongo_collection, empty_collection)
    found_post = mongo_collection.find_one({'_id': POST['_id']})
    assert found_post == POST
