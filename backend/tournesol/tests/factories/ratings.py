import factory
import factory.fuzzy

from core.tests.factories.user import UserFactory
from tournesol.models import ratings as ratings_models
from tournesol.tests.factories.video import VideoFactory


class ContributorRatingFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = ratings_models.ContributorRating

    entity = factory.SubFactory(VideoFactory)
    user = factory.SubFactory(UserFactory)
    is_public = False


class ContributorRatingCriteriaScoreFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = ratings_models.ContributorRatingCriteriaScore

    contributor_rating = factory.SubFactory(ContributorRatingFactory)
    criteria = "better_habits"
    score = factory.fuzzy.FuzzyDecimal(-10, 10)
