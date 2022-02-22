import datetime
import random
import string

import factory

from core.tests.factories.user import UserFactory
from tournesol.models import Entity, EntityCriteriaScore, VideoRateLater


def generate_youtube_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=11))


class VideoMetadataFactory(factory.DictFactory):
    source = "youtube"
    video_id = factory.LazyFunction(generate_youtube_id)
    name = factory.Sequence(lambda n: 'Entity title %s' % n)
    description = factory.Sequence(lambda n: 'Entity description %s' % n)
    duration = 60
    language = 'aa'
    uploader = factory.Sequence(lambda n: 'Uploader %s' % n)
    publication_date = factory.LazyFunction(lambda: datetime.date.today().isoformat())


class VideoFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Entity

    type = "video"
    metadata = factory.SubFactory(VideoMetadataFactory)
    video_id = factory.LazyAttribute(lambda e: e.metadata["video_id"])
    uid = factory.LazyAttribute(lambda e: f"yt:{e.metadata['video_id']}")
    name = factory.LazyAttribute(lambda e: e.metadata["name"])
    description = factory.LazyAttribute(lambda e: e.metadata["description"])
    duration = factory.LazyAttribute(
        lambda e: datetime.timedelta(seconds=e.metadata["duration"])
    )
    language = factory.LazyAttribute(lambda e: e.metadata["language"])
    uploader = factory.LazyAttribute(lambda e: e.metadata["uploader"])
    publication_date = factory.LazyAttribute(
        lambda e: datetime.date.fromisoformat(e.metadata["publication_date"])
    )


class VideoCriteriaScoreFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = EntityCriteriaScore

    entity = factory.SubFactory(VideoFactory)
    criteria = "better_habits"
    score = 1


class VideoRateLaterFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = VideoRateLater

    video = factory.SubFactory(VideoFactory)
    user = factory.SubFactory(UserFactory)
