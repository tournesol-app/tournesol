import factory
import factory.fuzzy

from core.tests.factories.user import UserFactory
from tournesol.models import comparisons as comparison_models
from tournesol.tests.factories.video import VideoFactory


class ComparisonFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = comparison_models.Comparison

    user = factory.SubFactory(UserFactory)
    video_1 = factory.SubFactory(VideoFactory)
    video_2 = factory.SubFactory(VideoFactory)

class ComparisonCriteriaScoreFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = comparison_models.ComparisonCriteriaScore

    comparison = factory.SubFactory(ComparisonFactory)
    criteria = "better_habits"
    score = factory.fuzzy.FuzzyDecimal(-10, 10)
