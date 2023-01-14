from dict_objectify import Array, Base, Bool, Integer, Text

from fixtures.models.commons import (ContactMixin, Country, Identifier,
                                     IdentifierMixin, MetadataMixin,
                                     Organisation, Publication)
from mongo_odm.models.base import MongoBase


class Project(Base, IdentifierMixin):
    relations_with = 'projects'

    title = Text(primary=True)


class Experience(Base):
    title = Text(primary=True)
    department = Text()
    from_year = Integer(primary=True)
    from_month = Integer(primary=True)
    to_year = Integer(primary=True)
    to_month = Integer(primary=True)
    present = Bool()

    organisation = Organisation()


class Education(Experience):
    pass


class ResearchGroup(Base, IdentifierMixin):
    relations_with = 'research_groups'

    name = Text()
    role = Text()
    contact = Bool()


class About(Base):
    about = Text(primary=True)
    language = Text(primary=True)
    label = Text()


class ResearcherMetadata(Base, MetadataMixin):
    normalized_names = Array(str)


class Researcher(MongoBase, ContactMixin, IdentifierMixin):
    first_name = Text()
    last_name = Text()
    full_name = Text()
    initials = Text()
    twitter_handle = Text()
    gender = Text()
    academic_title = Text()
    function_title = Text()
    paper_count = Integer()
    citation_count = Integer()
    estimated_citation_count = Integer()
    h_index = Integer()

    country = Country()

    other_names = Array(str)
    merged_names = Array(str)
    keywords = Array(str)
    interests = Array(str)
    collaboration_interests = Array(str)
    research_types = Array(str)

    experiences = Array(Experience)
    educations = Array(Education)
    organisations = Array(Organisation)
    projects = Array(Project)
    aliases = Array(Identifier)
    abouts = Array(About)
    publications = Array(Publication)
    research_groups = Array(ResearchGroup)

    _metadata = ResearcherMetadata()
