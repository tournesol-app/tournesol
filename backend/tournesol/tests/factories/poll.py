import factory
from factory.django import DjangoModelFactory

from tournesol.models import Criteria, CriteriaRank, Poll


class PollFactory(DjangoModelFactory):
    class Meta:
        model = Poll

    name = factory.Sequence(lambda n: "poll_%s" % n)
    entity_type = "video"


class CriteriaFactory(DjangoModelFactory):
    class Meta:
        model = Criteria
        django_get_or_create = ("name",)

    name = "better_habits"


class CriteriaRankFactory(DjangoModelFactory):
    class Meta:
        model = CriteriaRank

    criteria = factory.SubFactory(CriteriaFactory)
    poll = factory.SubFactory(PollFactory)
    rank = 0
    optional = False


class PollWithCriteriasFactory(PollFactory):
    criterias = factory.RelatedFactory(
        CriteriaRankFactory,
        factory_related_name='poll'
    )
