

import factory

from tournesol.models import comparisons as comparison_models
from tournesol.tests.factories.video import VideoFactory
from core.tests.factories.user import UserFactory


class ComparisonFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = comparison_models.Comparison

    user = factory.SubFactory(UserFactory)
    video_1 = factory.SubFactory(VideoFactory)
    video_2 = factory.SubFactory(VideoFactory)
