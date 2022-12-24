from typing import Any

import pytest

from dict_objectify.base.hash import __int_hash, dict_base_hash
from fixtures.models.commons import Country, Identifier, Organisation
from fixtures.models.researcher import Experience, Researcher
from mongo_odm.models.base import MongoBase

RESEARCHER_DICT_VER_1 = {'first_name': 'Test',
                         'identifiers': [
                             {"name": "fris",
                              "value": "94275885-8345-461e-8507-f866c968ebd5"},
                             {"name": "fris",
                              "value": "ed9226cc-7cb2-40f8-95f6-1b0d39695900"}],
                         'country': {'name': 'belgium',
                                     'code': 'be'},
                         'keywords': ['keyword_1', 'keyword_2'],
                         'experiences': [
                             {'title': 'Title',
                              'organisation': {'name': 'Name',
                                               'country': {
                                                   'code': 'be',
                                                   'name': 'belgium'}}}],
                         'created_at': '2020-04-16T13:33:17Z',
                         'updated_at': '2020-04-17T15:11:21Z'}

RESEARCHER_DICT_VER_2 = {'first_name': 'Test',
                         'created_at': '2019-03-16T13:33:17Z',
                         'updated_at': '2019-03-17T15:11:21Z',
                         'experiences': [
                             {'organisation': {'country': {'code': 'be',
                                                           'name': 'belgium'},
                                               'name': 'Name'},
                              'title': 'Title'}],
                         'keywords': ['keyword_2', 'keyword_1'],
                         'country': {'code': 'be',
                                     'name': 'belgium'},
                         'identifiers': [
                             {"name": "fris",
                              "value": "ed9226cc-7cb2-40f8-95f6-1b0d39695900"},
                             {"name": "fris",
                              "value": "94275885-8345-461e-8507-f866c968ebd5"}]}

RESEARCHER_DICT_VER_3 = {'first_name': 'Test',
                         'created_at': '2019-03-16T13:33:17Z',
                         'updated_at': '2019-03-17T15:11:21Z',
                         'experiences': [],
                         'keywords': ['keyword_2', 'keyword_1'],
                         'country': {'code': 'be',
                                     'name': 'belgium'},
                         'identifiers': [
                             {"name": "orcid",
                              "value": "94275885-8345-461e-8507"}]}

EXPERIENCE_DICT_1 = {'title': 'Title',
                     'present': True,
                     'organisation': {'name': 'Name',
                                      'country': {'code': 'be',
                                                  'name': 'belgium',
                                                  'normalized_name': 'nn1'}}}

EXPERIENCE_DICT_2 = {'title': 'Title',
                     'present': False,
                     'organisation': {'name': 'Name',
                                      'country': {'code': 'be',
                                                  'name': 'belgium',
                                                  'normalized_name': 'nn2'}}}


@pytest.fixture()
def researcher_1() -> Researcher:
    country = Country(name=RESEARCHER_DICT_VER_1['country']['name'],
                      code=RESEARCHER_DICT_VER_1['country']['code'])
    identifiers = [Identifier(name=identifier['name'],
                              value=identifier['value'])
                   for identifier in RESEARCHER_DICT_VER_1['identifiers']]
    experiences = [Experience(
        title=RESEARCHER_DICT_VER_1['experiences'][0]['title'],
        organisation=Organisation(
            name=RESEARCHER_DICT_VER_1[
                'experiences'][0]['organisation']['name'],
            country=country))]
    return Researcher(
        first_name=RESEARCHER_DICT_VER_1['first_name'],
        keywords=RESEARCHER_DICT_VER_1['keywords'],
        experiences=experiences,
        country=country,
        identifiers=identifiers)


@pytest.mark.parametrize('value,length,expected_hash',
                         [('test_1',
                           20,
                           45036590271683491959),
                          ('test_2',
                           20,
                           17739181516819817863)])
def test_int_hash(value: str, length: int, expected_hash: int):
    calculated_hash = __int_hash(value)
    assert expected_hash == calculated_hash
    assert len(str(calculated_hash)) == length


@pytest.mark.parametrize('value_1,value_2',
                         [('100',
                           100),
                          ('True',
                           True),
                          (['1', 'True'],
                           [True, 1]),
                          (RESEARCHER_DICT_VER_1['identifiers'],
                           RESEARCHER_DICT_VER_2['identifiers'])])
def test_dict_base_hash_compare(value_1: Any, value_2: Any):
    assert dict_base_hash(value_1) == dict_base_hash(value_2)


def test_mongo_doc_obj_hash_value(researcher_1: Researcher):
    dct = RESEARCHER_DICT_VER_1.copy()
    del dct['created_at']
    del dct['updated_at']

    expected_hash = str(dict_base_hash(dct))

    assert researcher_1._hash
    assert researcher_1._hash == expected_hash


def test_mongo_obj_init(researcher_1: Researcher):
    assert researcher_1._hash
    assert researcher_1._hash == Researcher(
        data_dict=RESEARCHER_DICT_VER_1)._hash
    assert Researcher(
        data_dict=RESEARCHER_DICT_VER_1)._hash == Researcher(
        data_dict=RESEARCHER_DICT_VER_2)._hash


def test_mongo_obj_update_hash_changes(researcher_1: Researcher):
    hash_before_update = researcher_1._hash
    first_name_before_update = researcher_1.first_name

    researcher_1.first_name = 'Updated_name'
    researcher_1.check_hash_and_update()

    assert researcher_1._hash != hash_before_update

    researcher_1.first_name = first_name_before_update
    researcher_1.check_hash_and_update()

    assert researcher_1._hash == hash_before_update


def test_empty_mongo_obj():
    assert Researcher()._hash == '0'
    assert Researcher(data_dict={})._hash == '0'


def test_base_obj_hashes():
    experience_1 = Experience(data_dict=EXPERIENCE_DICT_1)
    experience_2 = Experience(data_dict=EXPERIENCE_DICT_2)

    assert experience_1.__hash__() == experience_2.__hash__()


def test_different_hashes():
    researcher_2 = Researcher(data_dict=RESEARCHER_DICT_VER_2)
    researcher_3 = Researcher(data_dict=RESEARCHER_DICT_VER_3)

    assert researcher_2._hash != researcher_3._hash


def test_eq(researcher_1: Researcher):
    researcher_2 = Researcher(data_dict=RESEARCHER_DICT_VER_2)

    assert researcher_1 == researcher_2

    researcher_1_alt = Researcher(data_dict=RESEARCHER_DICT_VER_1)

    assert researcher_1 == researcher_1_alt

    experience_1 = Experience(data_dict=EXPERIENCE_DICT_1)
    experience_2 = Experience(data_dict=EXPERIENCE_DICT_2)

    assert experience_1 == experience_2


def test_nested():
    obj1 = {'a': [{'aa': 5, 'ab': [5, 6, {'aaa': [4, 5, 6]}]},
                  {'aa': 7, 'ab': [1, 2, 3]}]}
    obj2 = {'a': [{'aa': 7, 'ab': [1, 2, 3]},
                  {'aa': 5, 'ab': [5, 6, {'aaa': [6, 5, 4]}]}]}
    base_obj1 = MongoBase(data_dict=obj1)
    base_obj2 = MongoBase(data_dict=obj2)
    assert base_obj1._hash == base_obj2._hash


def test_duplicates():
    obj1 = {'a': [1, 2, 3]}
    obj2 = {'a': [1, 2, 3, 1]}
    base_obj1 = MongoBase(data_dict=obj1)
    base_obj2 = MongoBase(data_dict=obj2)
    assert base_obj1._hash != base_obj2._hash
