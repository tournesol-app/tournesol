import datetime
import random
import string

import factory

from core.tests.factories.user import UserFactory
from tournesol.models import entity as entity_models


def generate_youtube_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=11))


class VideoFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = entity_models.Entity

    video_id = factory.LazyFunction(generate_youtube_id)
    name = factory.Sequence(lambda n: 'Entity title %s' % n)
    description = factory.Sequence(lambda n: 'Entity description %s' % n)
    duration = factory.LazyAttribute(lambda _: datetime.timedelta(seconds=60))
    language = 'aa'
    uploader = factory.Sequence(lambda n: 'Uploader %s' % n)
    publication_date = factory.LazyFunction(datetime.datetime.now)


class VideoCriteriaScoreFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = entity_models.EntityCriteriaScore

    video = factory.SubFactory(VideoFactory)
    criteria = "better_habits"
    score = 1


class VideoRateLaterFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = entity_models.VideoRateLater

    video = factory.SubFactory(VideoFactory)
    user = factory.SubFactory(UserFactory)
