"""
All test cases of the `EntityPollRating` model.
"""
import random

from django.test import TestCase

from core.tests.factories.user import UserFactory
from tournesol.models import Comparison, EntityPollRating
from tournesol.models.entity_context import EntityContext
from tournesol.tests.factories.entity import VideoFactory
from tournesol.tests.factories.poll import PollFactory
from tournesol.tests.factories.ratings import (
    ContributorRatingCriteriaScoreFactory,
    ContributorRatingFactory,
)


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

    def test_unsafe_recommendation_reasons(self):
        entity = VideoFactory()
        entity_poll_rating = EntityPollRating.objects.create(
            poll=self.poll,
            entity=entity,
            tournesol_score=None,
            sum_trust_scores=0.0,
        )

        unsafe_reasons = entity_poll_rating.unsafe_recommendation_reasons
        self.assertEqual(len(unsafe_reasons), 1)
        self.assertIn('insufficient_tournesol_score', unsafe_reasons)

        entity_poll_rating.tournesol_score = 0.0
        entity_poll_rating.save(update_fields=["tournesol_score"])
        # We re-assign entity_poll_rating, because
        # unsafe_recommendation_reasons is a cached property tied ot its model
        # instance.
        entity_poll_rating = EntityPollRating.objects.get(pk=entity_poll_rating.pk)

        unsafe_reasons = entity_poll_rating.unsafe_recommendation_reasons
        self.assertEqual(len(unsafe_reasons), 2)
        self.assertIn('insufficient_tournesol_score', unsafe_reasons)
        self.assertIn('insufficient_trust', unsafe_reasons)

    def test_unsafe_recommendation_reasons_moderation(self):
        entity = VideoFactory()
        entity_poll_rating = EntityPollRating.objects.create(
            poll=self.poll,
            entity=entity,
            tournesol_score=40,
            sum_trust_scores=40,
        )

        # The predicate doesn't match any entity.
        self.poll.all_entity_contexts.create(
            name="orphan_context",
            origin=EntityContext.ASSOCIATION,
            predicate={"video_id": "_"},
            unsafe=True,
            enabled=True
        )
        self.assertEqual(len(entity_poll_rating.unsafe_recommendation_reasons), 0)

        self.poll.all_entity_contexts.all().delete()
        entity_poll_rating = EntityPollRating.objects.get(pk=entity_poll_rating.pk)

        # The context isn't flagged as unsafe.
        self.poll.all_entity_contexts.create(
            name="context_safe",
            origin=EntityContext.ASSOCIATION,
            predicate={"video_id": entity.metadata["video_id"]},
            unsafe=False,
            enabled=True
        )
        self.assertEqual(len(entity_poll_rating.unsafe_recommendation_reasons), 0)

        self.poll.all_entity_contexts.all().delete()
        entity_poll_rating = EntityPollRating.objects.get(pk=entity_poll_rating.pk)

        # The context is not enabled.
        self.poll.all_entity_contexts.create(
            name="context_unsafe_disabled",
            origin=EntityContext.ASSOCIATION,
            predicate={"video_id": entity.metadata["video_id"]},
            unsafe=True,
            enabled=False
        )
        self.assertEqual(len(entity_poll_rating.unsafe_recommendation_reasons), 0)

        self.poll.all_entity_contexts.all().delete()
        entity_poll_rating = EntityPollRating.objects.get(pk=entity_poll_rating.pk)

        self.poll.all_entity_contexts.create(
            name="context_unsafe_enabled",
            origin=EntityContext.ASSOCIATION,
            predicate={"video_id": entity.metadata["video_id"]},
            unsafe=True,
            enabled=True
        )

        unsafe_reasons = entity_poll_rating.unsafe_recommendation_reasons
        self.assertEqual(len(unsafe_reasons), 1)
        self.assertIn('moderation_by_association', unsafe_reasons)


class EntityPollRatingBulkTrustScoreUpdate(TestCase):
    """
    TestCase of the `EntityPollRatingTestCase` model.
    """

    def setUp(self):
        self.poll = PollFactory()
        self.user_a = UserFactory(trust_score=0.01)
        self.user_b = UserFactory(trust_score=0.9)
        self.user_c = UserFactory(trust_score=0.5)
        self.video_1 = VideoFactory()
        self.video_2 = VideoFactory()
        self.video_3 = VideoFactory()
        rating_a_1 = ContributorRatingFactory(poll=self.poll, user=self.user_a, entity=self.video_1)
        ContributorRatingCriteriaScoreFactory(contributor_rating=rating_a_1)
        rating_a_2 = ContributorRatingFactory(poll=self.poll, user=self.user_a, entity=self.video_2)
        ContributorRatingCriteriaScoreFactory(contributor_rating=rating_a_2)
        rating_b_1 = ContributorRatingFactory(poll=self.poll, user=self.user_b, entity=self.video_1)
        ContributorRatingCriteriaScoreFactory(contributor_rating=rating_b_1)
        rating_c_1 = ContributorRatingFactory(poll=self.poll, user=self.user_c, entity=self.video_1)

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
        self.assertAlmostEqual(self.entity_poll_rating_1.sum_trust_scores, 0.91)
        self.entity_poll_rating_2.refresh_from_db()
        self.assertAlmostEqual(self.entity_poll_rating_2.sum_trust_scores, 0.01)
        self.entity_poll_rating_3.refresh_from_db()
        self.assertAlmostEqual(self.entity_poll_rating_3.sum_trust_scores, 0.)

    def test_update_sum_trust_without_batch(self):
        EntityPollRating.bulk_update_sum_trust_scores(self.poll, batch_size=None)
        self.check_sum_trust_scores_are_correctly_updated()

    def test_update_sum_trust_with_batch_equal_one(self):
        EntityPollRating.bulk_update_sum_trust_scores(self.poll, batch_size=1)
        self.check_sum_trust_scores_are_correctly_updated()

    def test_update_sum_trust_with_default_batch(self):
        EntityPollRating.bulk_update_sum_trust_scores(self.poll)
        self.check_sum_trust_scores_are_correctly_updated()


class EntityPollRatingBulkTrustScoreUpdateOnRandomData(TestCase):
    """
    TestCase of the `EntityPollRatingTestCase` model.
    """

    def setUp(self):
        self.poll = PollFactory()
        N_USERS = 100
        N_VIDEOS = 10
        RATING_PROBABILITY = 0.5  # probability that a user u rated a video v
        SCORE_PROBABILITY = 0.9  # probability that a score exists for a given rating
        self.users = [UserFactory(trust_score=random.random()) for _ in range(N_USERS)]
        self.videos = [VideoFactory() for _ in range(N_VIDEOS)]
        self.ratings = [
            ContributorRatingFactory(poll=self.poll, user=u, entity=v)
            for u in self.users
            for v in self.videos
            if random.random() < RATING_PROBABILITY
        ]
        self.scores = [
            ContributorRatingCriteriaScoreFactory(contributor_rating=r)
            for r in self.ratings
            if random.random() < SCORE_PROBABILITY
        ]
        self.entity_poll_ratings = [
            EntityPollRating.objects.create(entity=v, poll=self.poll)
            for v in self.videos
        ]

    def test_same_trust_scores_with_or_not_batches(self):
        EntityPollRating.bulk_update_sum_trust_scores(self.poll, batch_size=None)
        for epr in self.entity_poll_ratings: epr.refresh_from_db()
        sum_trust_scores_no_batch = [epr.sum_trust_scores for epr in self.entity_poll_ratings]
        EntityPollRating.bulk_update_sum_trust_scores(self.poll, batch_size=100)
        for epr in self.entity_poll_ratings: epr.refresh_from_db()
        sum_trust_scores_batch = [epr.sum_trust_scores for epr in self.entity_poll_ratings]
        for a,b in zip(sum_trust_scores_no_batch, sum_trust_scores_batch):
            self.assertAlmostEqual(a, b)
