import factory.django

from tournesol.models import EntityCriteriaScore as EntityCriteriaScoreModels, Poll
from tournesol.tests.factories.entity import VideoFactory


class EntityCriteriaScoreFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EntityCriteriaScoreModels

    poll = factory.LazyAttribute(lambda p: Poll.default_poll())
    entity = factory.SubFactory(VideoFactory)
