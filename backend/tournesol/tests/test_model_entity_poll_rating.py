"""
All test cases of the `EntityPollRating` model.
"""

from django.test import TestCase

from core.tests.factories.user import UserFactory
from tournesol.models import Comparison, EntityPollRating
from tournesol.tests.factories.entity import VideoFactory
from tournesol.tests.factories.poll import PollFactory
from tournesol.tests.factories.ratings import ContributorRatingFactory


class EntityPollRatingTestCase(TestCase):
    """
    TestCase of the `EntityPollRatingTestCase` model.
    """

    _user = "username"

    def setUp(self):
        self.poll = PollFactory()
        self.user = UserFactory(username=self._user)
        self.video_1 = VideoFactory()
        self.video_2 = VideoFactory()

        self.entity_poll_rating_1 = EntityPollRating.objects.create(
            entity=self.video_1, poll=self.poll
        )
        self.entity_poll_rating_2 = EntityPollRating.objects.create(
            entity=self.video_2, poll=self.poll
        )
        self.comparaison = Comparison.objects.create(
            entity_1=self.video_1, entity_2=self.video_2, poll=self.poll, user=self.user
        )

        self.entity_poll_rating_1.update_n_ratings()
        self.entity_poll_rating_2.update_n_ratings()

    def test_update_n_ratings_n_comparisons(self):
        """
        Given a new comparison including video_1 and a new video,
        When we run update_n_ratings() on video_1 and video_2
        Then the video_1.n_comparisons number increases by 1,
        Then the video_2 ratings stays the same.
        """
        # [GIVEN] Add new comparison between video 1 and video 3
        self.video_3 = VideoFactory()
        Comparison.objects.create(
            entity_1=self.video_1, entity_2=self.video_3, poll=self.poll, user=self.user
        )

        # [WHEN] We update the ratings of video 1 and video 2
        self.entity_poll_rating_1.update_n_ratings()
        self.entity_poll_rating_2.update_n_ratings()

        # [THEN] Only video 1 n_comparisons increases
        updated_rating_1 = self.video_1.all_poll_ratings.filter(poll=self.poll).first()
        updated_rating_2 = self.video_2.all_poll_ratings.filter(poll=self.poll).first()

        self.assertEqual(updated_rating_1.n_comparisons, 2)
        self.assertEqual(updated_rating_1.n_contributors, 1)
        self.assertEqual(updated_rating_2.n_comparisons, 1)
        self.assertEqual(updated_rating_2.n_contributors, 1)

    def test_update_n_ratings_n_contributors(self):
        """
        Given a new user,
        Given a new comparison including video_1 and a new video
        When we run update_n_ratings() on video_1 and video_2
        Then the video_1.n_comparisons number increases by 1,
        Then the video_1.n_contributors number increases by 1,
        Then the video_2 ratings stays the same.
        """
        # [GIVEN] Add new user and a comparison between video 1 and video 3
        self.user_2 = UserFactory(username="username_2")
        self.video_3 = VideoFactory()
        Comparison.objects.create(
            entity_1=self.video_1,
            entity_2=self.video_3,
            poll=self.poll,
            user=self.user_2,
        )

        # [WHEN] We update the entity poll ratings
        self.entity_poll_rating_1.update_n_ratings()
        self.entity_poll_rating_2.update_n_ratings()

        # [THEN] Only video 1 n_comparisons and n_contributors increase
        updated_rating_1 = self.video_1.all_poll_ratings.filter(poll=self.poll).first()
        updated_rating_2 = self.video_2.all_poll_ratings.filter(poll=self.poll).first()
        self.assertEqual(updated_rating_1.n_comparisons, 2)
        self.assertEqual(updated_rating_1.n_contributors, 2)
        self.assertEqual(updated_rating_2.n_comparisons, 1)
        self.assertEqual(updated_rating_2.n_contributors, 1)

class EntityPollRatingBulkTrustScoreUpdate(TestCase):
    """
    TestCase of the `EntityPollRatingTestCase` model.
    """

    def setUp(self):
        self.poll = PollFactory()
        self.user_a = UserFactory(trust_score=0.01)
        self.user_b = UserFactory(trust_score=0.9)
        self.video_1 = VideoFactory()
        self.video_2 = VideoFactory()
        self.video_3 = VideoFactory()
        ContributorRatingFactory(poll=self.poll, user=self.user_a, entity=self.video_1)
        ContributorRatingFactory(poll=self.poll, user=self.user_a, entity=self.video_2)
        ContributorRatingFactory(poll=self.poll, user=self.user_b, entity=self.video_1)

        self.entity_poll_rating_1 = EntityPollRating.objects.create(
            entity=self.video_1, poll=self.poll
        )
        self.entity_poll_rating_2 = EntityPollRating.objects.create(
            entity=self.video_2, poll=self.poll
        )
        self.entity_poll_rating_3 = EntityPollRating.objects.create(
            entity=self.video_3, poll=self.poll
        )

    def check_sum_trust_scores_are_correctly_updated(self):
        self.entity_poll_rating_1.refresh_from_db()
        assert self.entity_poll_rating_1.sum_trust_scores == 0.91
        self.entity_poll_rating_2.refresh_from_db()
        assert self.entity_poll_rating_2.sum_trust_scores == 0.01
        self.entity_poll_rating_3.refresh_from_db()
        assert self.entity_poll_rating_3.sum_trust_scores == 0.

    def test_update_sum_trust_without_batch(self):
        EntityPollRating.bulk_update_sum_trust_scores(self.poll, batch_size=None)
        self.check_sum_trust_scores_are_correctly_updated()

    def test_update_sum_trust_with_batch_equal_one(self):
        EntityPollRating.bulk_update_sum_trust_scores(self.poll, batch_size=1)
        self.check_sum_trust_scores_are_correctly_updated()

    def test_update_sum_trust_with_default_batch(self):
        EntityPollRating.bulk_update_sum_trust_scores(self.poll)
        self.check_sum_trust_scores_are_correctly_updated()
