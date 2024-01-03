import datetime
import random
import string
from typing import Optional, Union

import factory
from django.conf import settings

from core.tests.factories.user import UserFactory
from tournesol.entities.video import TYPE_VIDEO
from tournesol.models import Entity, EntityCriteriaScore, Poll, RateLater
from tournesol.utils.constants import MEHESTAN_MAX_SCALED_SCORE


class EntityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Entity

    uid = factory.Sequence(lambda n: "uid_%s" % n)

    @staticmethod
    def get_safe_tournesol_score():
        min_score = settings.RECOMMENDATIONS_MIN_TOURNESOL_SCORE + 1
        max_score = MEHESTAN_MAX_SCALED_SCORE
        return random.uniform(min_score, max_score)

    @classmethod
    def create(
        cls,
        *args,
        make_safe_for_poll: Union[bool, Poll] = True,
        n_comparisons: int = 0,
        n_contributors: int = 0,
        tournesol_score: Optional[float] = None,
        **kwargs
    ):
        """
        If `make_safe_for_poll` is True, the entity will be made safe for the default Poll by
        creating an EntityPollRating with a high `sum_trust_score`. If a poll is provided it will
        be made safe for the specified Poll. If something else is provided, nothing will be done.
        """
        entity = super().create(*args, **kwargs)
        create_rating_for_poll = None
        if make_safe_for_poll is True:
            create_rating_for_poll = Poll.default_poll()
        elif make_safe_for_poll is False and tournesol_score is not None:
            create_rating_for_poll = Poll.default_poll()
        elif isinstance(make_safe_for_poll, Poll):
            create_rating_for_poll = make_safe_for_poll

        if create_rating_for_poll is not None:
            from tournesol.tests.factories.entity_poll_rating import EntityPollRatingFactory

            EntityPollRatingFactory(
                sum_trust_scores=settings.RECOMMENDATIONS_MIN_TRUST_SCORES + 1,
                entity=entity,
                poll=create_rating_for_poll,
                tournesol_score=(
                    cls.get_safe_tournesol_score()
                    if tournesol_score is None
                    else tournesol_score
                ),
                n_comparisons=n_comparisons,
                n_contributors=n_contributors,
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
    views = 1000


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
