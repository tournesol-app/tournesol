import factory.django

from core.tests.factories.user import UserFactory
from tournesol.models import ContributorScaling, Poll


class ContributorScalingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ContributorScaling

    user = factory.SubFactory(UserFactory)
    poll = factory.LazyAttribute(lambda p: Poll.default_poll())
