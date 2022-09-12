"""
All test cases of the `EntityPollRating` model.
"""

from django.test import TestCase

from core.tests.factories.user import UserFactory
from tournesol.models import Comparison, EntityPollRating
from tournesol.tests.factories.entity import VideoFactory
from tournesol.tests.factories.poll import PollFactory


class EntityPollRatingTestCase(TestCase):
    """
    TestCase of the `EntityPollRatingTestCase` model.
    """

    _user = "username"

    def setUp(self):
        self.poll = PollFactory()
        self.video_1 = VideoFactory()
        self.video_2 = VideoFactory()
        self.user = UserFactory(username=self._user)

        self.comparaison = Comparison.objects.create(entity_1=self.video_1, entity_2=self.video_2,
                                                     poll=self.poll, user=self.user)
        self.entity_poll_rating_1 = EntityPollRating.objects.create(entity=self.video_1,
                                                                    poll=self.poll)
        self.entity_poll_rating_2 = EntityPollRating.objects.create(entity=self.video_2,
                                                                    poll=self.poll)

        self.entity_poll_rating_1.update_n_ratings()
        self.entity_poll_rating_2.update_n_ratings()

    def test_update_n_ratings(self):
        # [GIVEN] Add new comparison between viode 1 and a third video
        self.video_3 = VideoFactory()
        Comparison.objects.create(entity_1=self.video_1, entity_2=self.video_3, poll=self.poll,
                                  user=self.user)

        # [WHEN] We update the entity poll ratings
        self.entity_poll_rating_1.update_n_ratings()
        self.entity_poll_rating_2.update_n_ratings()

        # [THEN] Only video nb comparison has been increased
        updated_rating_1 = self.video_1.all_poll_ratings.filter(poll=self.poll).first()
        updated_rating_2 = self.video_2.all_poll_ratings.filter(poll=self.poll).first()
        self.assertEqual(updated_rating_1.n_comparisons, 2)
        self.assertEqual(updated_rating_1.n_contributors, 1)
        self.assertEqual(updated_rating_2.n_comparisons, 1)
        self.assertEqual(updated_rating_2.n_contributors, 1)

    def test_update_n_ratings_n_contributors(self):
        # [GIVEN] Add new comparison between viode 1 and video 2 with a second user
        self.user_2 = UserFactory(username="username_2")
        self.video_3 = VideoFactory()
        Comparison.objects.create(entity_1=self.video_1, entity_2=self.video_3, poll=self.poll,
                                  user=self.user_2)

        # [WHEN] We update the entity poll ratings
        self.entity_poll_rating_1.update_n_ratings()
        self.entity_poll_rating_2.update_n_ratings()

        # [THEN] Only video 1 nb comparison and nb contributors has been increased
        updated_rating_1 = self.video_1.all_poll_ratings.filter(poll=self.poll).first()
        updated_rating_2 = self.video_2.all_poll_ratings.filter(poll=self.poll).first()
        self.assertEqual(updated_rating_1.n_comparisons, 2)
        self.assertEqual(updated_rating_1.n_contributors, 2)
        self.assertEqual(updated_rating_2.n_comparisons, 1)
        self.assertEqual(updated_rating_2.n_contributors, 1)
