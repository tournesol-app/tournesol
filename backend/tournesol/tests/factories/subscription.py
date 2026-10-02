import random
import string

import factory

from core.tests.factories.user import UserFactory
from tournesol.models.entity_source import EntitySource
from tournesol.models.subscription import Subscription


def generate_youtube_channel_id():
    return "UC" + "".join(
        random.choices(string.ascii_letters + string.digits + "-_", k=22)
    )


class EntitySourceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EntitySource

    uid = factory.LazyFunction(lambda: f"yt:{generate_youtube_channel_id()}")
    metadata = factory.Sequence(lambda n: {"name": f"Channel {n}"})


class SubscriptionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Subscription

    user = factory.SubFactory(UserFactory)
    entity_source = factory.SubFactory(EntitySourceFactory)
