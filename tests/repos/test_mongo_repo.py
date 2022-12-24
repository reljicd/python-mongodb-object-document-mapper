import pytest

from fixtures.models.commons import Identifier, Source
from fixtures.models.researcher import Researcher
from mongo_odm.repos.repo import MongoRepo
from mongo_odm.repos.repos import MongoRepos

COLLECTION = 'researchers'
COUNT = 111


@pytest.fixture(scope='module')
def researchers_repo() -> MongoRepo:
    return MongoRepos.repo(COLLECTION)


@pytest.fixture()
def reset_mongo(researchers_repo: MongoRepo) -> None:
    for repo in MongoRepos.all_repos():
        repo.delete_all()

    for i in range(1, COUNT + 1):
        researchers_repo.insert_obj(
            Researcher(
                _id=str(i),
                first_name=f'Name_{i}',
                identifiers=[Identifier(name='test', value=str(i))],
                sources=[Source(name='test', value=str(i))]
            )
        )


def test_count(researchers_repo: MongoRepo, reset_mongo):
    assert researchers_repo.count() == COUNT


def test_exists_one(researchers_repo: MongoRepo, reset_mongo):
    researcher = next(researchers_repo.all_objs())
    assert researchers_repo.exists_one({'_hash': researcher._hash})
    assert not researchers_repo.exists_one({'_hash': '-1'})


def test_all_parallel(researchers_repo: MongoRepo, reset_mongo):
    researchers = list(researchers_repo.all_parallel())
    assert len(researchers) == COUNT
