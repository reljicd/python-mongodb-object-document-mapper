from dict_objectify.base.base import Base, MixinBase
from dict_objectify.fields.array import Array
from dict_objectify.fields.bool import Bool
from dict_objectify.fields.date import Datetime
from dict_objectify.fields.enum import EnumField
from dict_objectify.fields.float import Float
from dict_objectify.fields.integer import Integer
from dict_objectify.fields.text import Text


class Identifier(Base):
    name = EnumField(primary=True, nullable=False,
                     enumeration=['orcid', 'ringgold', 'fris', 'test'])
    value = Text(primary=True, nullable=False)


class Contact(Base):
    category = Text(primary=True)
    value = Text(primary=True)


class Source(Base):
    name = EnumField(primary=True, nullable=False,
                     enumeration=['orcid', 'ringgold', 'fris', 'test'])
    value = Text(primary=True, nullable=False)
    url = Text()


class Country(Base):
    name = Text()
    code = Text(primary=True)


class Title(Base):
    title = Text(primary=True)
    language = Text(primary=True)


class IdentifierMixin(MixinBase):
    identifiers = Array(Identifier)
    unreliable_identifiers = Array(Identifier)


class MetadataMixin(MixinBase):
    sources_hash = Array(str)


class ContactMixin(MixinBase):
    contacts = Array(Contact)


class Url(Base):
    url = Text(nullable=False)
    domain = Text()
    note = Text()


class Organisation(Base, IdentifierMixin):
    relations_with = 'organisations'

    name = Text(primary=True)
    normalized_name = Text()

    present = Bool()

    country = Country(primary=True)

    state = Text()
    district = Text()
    city = Text()
    zipcode = Text()
    street = Text()

    urls = Array(Url)


class Participant(Base, IdentifierMixin, ContactMixin):
    relations_with = 'researchers'

    first_name = Text()
    last_name = Text()
    full_name = Text()
    collective_name = Text()
    initials = Text()

    role = Text()

    country = Country()

    other_names = Array(str, 'subjects')

    organisations = Array(Organisation)


class Publication(Base, IdentifierMixin):
    relations_with = 'publications'

    titles = Array(Title)
    authors = Array(Participant)


class Ranking(Base):
    name = Text(nullable=False)
    version = Text(nullable=False)

    version_timestamp = Datetime(nullable=False)

    url = Text()

    rank = Integer()
    upper_rank = Integer()

    score = Float()
    upper_score = Float()
