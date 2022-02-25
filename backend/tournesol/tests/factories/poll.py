import factory
from factory import fuzzy

from tournesol.models import Criteria, CriteriaRank, Poll


class PollFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Poll

    name = factory.Sequence(lambda n: "Poll #%s" % n)
    entity_type = "Video"


class CriteriaRankFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CriteriaRank

    criteria = factory.LazyAttribute(lambda x:  Criteria.objects.get_or_create(name="better_habits")[0])
    poll = factory.SubFactory(PollFactory)
    rank = 0
    optional = False

class PollWithCriterasFactory(PollFactory):
   criteras = factory.RelatedFactory(
        CriteriaRankFactory,
        factory_related_name='poll'
    )
