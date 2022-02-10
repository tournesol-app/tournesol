import factory
from factory import fuzzy

from core.tests.factories.user import UserFactory
from tournesol.models import Poll
from tournesol.models import comparisons as comparison_models
from tournesol.tests.factories.video import VideoFactory


class ComparisonFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = comparison_models.Comparison

    poll = factory.LazyAttribute(lambda n: Poll.default_poll())
    user = factory.SubFactory(UserFactory)
    entity_1 = factory.SubFactory(VideoFactory)
    entity_2 = factory.SubFactory(VideoFactory)


class ComparisonCriteriaScoreFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = comparison_models.ComparisonCriteriaScore

    comparison = factory.SubFactory(ComparisonFactory)
    criteria = "better_habits"
    score = fuzzy.FuzzyDecimal(-10, 10)
