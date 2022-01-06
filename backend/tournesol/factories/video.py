import datetime

import factory

from tournesol.models import video as video_models
from tournesol.utils import video_id


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
