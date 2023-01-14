from dict_objectify import Array, Base, Bool, Datetime, Text

from fixtures.models.commons import (ContactMixin, Country, Identifier,
                                     IdentifierMixin, MetadataMixin, Ranking,
                                     Url)
from mongo_odm.models.base import MongoBase


class Tier(Base):
    name = Text(primary=True)
    value = Text(primary=True)


class OtherName(Base):
    name = Text(primary=True)
    note = Text(primary=True)


class OrganisationMetadata(Base, MetadataMixin):
    rankings = Array(Ranking)


class Organisation(MongoBase, ContactMixin, IdentifierMixin):
    parent_id = Text()
    name = Text()
    state = Text()
    post_code = Text()
    city = Text()
    street = Text()
    category = Text()
    sub_category = Text()
    foundation_date = Datetime()
    main_tier = Bool()

    country = Country()

    keywords = Array(str)
    member_ids = Array(str)
    manual_names = Array(str)
    normalized_names = Array(str)

    other_names = Array(OtherName)
    alt_identifiers = Array(Identifier)
    tiers = Array(Tier)
    urls = Array(Url)

    _metadata = OrganisationMetadata()
