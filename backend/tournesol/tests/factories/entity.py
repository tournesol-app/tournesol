import datetime
import random
import string

import factory

from core.tests.factories.user import UserFactory
from tournesol.models import Entity, EntityCriteriaScore, Poll, RateLater


class EntityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Entity

    uid = factory.Sequence(lambda n: "uid_%s" % n)


def generate_youtube_id():
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=11))


class VideoMetadataFactory(factory.DictFactory):
    source = "youtube"
    video_id = factory.LazyFunction(generate_youtube_id)
    name = factory.Sequence(lambda n: "Entity title %s" % n)
    description = factory.Sequence(lambda n: "Entity description %s" % n)
    duration = 60
    language = "aa"
    uploader = factory.Sequence(lambda n: "Uploader %s" % n)
    publication_date = factory.LazyFunction(lambda: datetime.date.today().isoformat())


class VideoFactory(EntityFactory):
    type = "video"
    metadata = factory.SubFactory(VideoMetadataFactory)
    uid = factory.LazyAttribute(lambda e: f"yt:{e.metadata['video_id']}")


class VideoCriteriaScoreFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EntityCriteriaScore

    entity = factory.SubFactory(VideoFactory)
    criteria = "better_habits"
    score = 1


class RateLaterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RateLater

    entity = factory.SubFactory(VideoFactory)
    user = factory.SubFactory(UserFactory)
    poll = factory.LazyAttribute(lambda n: Poll.default_poll())
