import datetime

import factory

from tournesol.models import video as video_models
from tournesol.utils import video_id
from core.tests.factories.user import UserFactory


class VideoFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = video_models.Video

    video_id = factory.LazyFunction(video_id.generate_youtube_id)
    name = factory.Sequence(lambda n: 'Video title %s' % n)
    description = factory.Sequence(lambda n: 'Video description %s' % n)
    duration = factory.LazyAttribute(lambda _: datetime.timedelta(seconds=60))
    language = 'aa'
    uploader = factory.Sequence(lambda n: 'Uploader %s' % n)
    publication_date = factory.LazyFunction(datetime.datetime.now)


class VideoCriteriaScoreFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = video_models.VideoCriteriaScore

    video = factory.SubFactory(VideoFactory)
    criteria = "better_habits"
    score = 1


class VideoRateLaterFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = video_models.VideoRateLater

    video = factory.SubFactory(VideoFactory)
    user = factory.SubFactory(UserFactory)
