import datetime
import random
import string
from typing import Union

import factory

from core.tests.factories.user import UserFactory
from settings.settings import RECOMMENDATIONS_MIN_TRUST_SCORES
from tournesol.entities.video import TYPE_VIDEO
from tournesol.models import Entity, EntityCriteriaScore, Poll, RateLater
from tournesol.utils.constants import MEHESTAN_MAX_SCALED_SCORE


class EntityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Entity

    uid = factory.Sequence(lambda n: "uid_%s" % n)

    @classmethod
    def create(cls, *args, make_safe_for_poll: Union[bool, Poll] = True, **kwargs):
        entity = super().create(*args, **kwargs)
        """
        If `make_safe_for_poll` is True, the entity will be made safe for the default Poll by
        creating an EntityPollRating with a high `sum_trust_score`. If a poll is provided it will
        be made safe for the specified Poll. If something else is provided, nothing will be done.
        """
        if make_safe_for_poll is True:
            make_safe_for_poll = Poll.default_poll()
        if isinstance(make_safe_for_poll, Poll):
            from tournesol.tests.factories.entity_poll_rating import EntityPollRatingFactory
            EntityPollRatingFactory(
                sum_trust_scores=RECOMMENDATIONS_MIN_TRUST_SCORES + 1,
                entity=entity,
                poll=make_safe_for_poll,
                tournesol_score=1 + (MEHESTAN_MAX_SCALED_SCORE - 1) * random.random()
            )
        return entity


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
    type = TYPE_VIDEO
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
