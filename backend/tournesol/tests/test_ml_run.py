"""
Test cases related to how "ml_train" computes individual and global scores based on comparisons

These tests use `TransactionTestCase` as their base class instead of the usual `TestCase`.

`TestCase` uses an open transaction for each test case: the transaction is never committed and changes
applied in the db during the test case will be rollbacked in a cheap manner. However this approach
is not suitable to run "ml_train" which spawns multiple threads with independent connections to the database
(these threads won't see the changes applied by the non-committed transaction).
That's why `TransactionTestCase` is required here.

As `TransactionTestCase` allows to commmit changes into the database, its default behavior is to reset
the database between each test case. That would delete all data from the test database, including
the default Poll and criteria, defined by the database migrations.
For tests that depend on this default Poll, `serialized_rollback = True` must be used to reload the
initial state of the database after each test.

Find more details on https://docs.djangoproject.com/en/4.0/topics/testing/overview/#rollback-emulation
"""
from django.core.management import call_command
from django.test import TransactionTestCase, override_settings

from core.models import EmailDomain
from core.tests.factories.user import UserFactory
from tournesol.models import (
    ContributorRating,
    ContributorRatingCriteriaScore,
    EntityCriteriaScore,
    EntityPollRating,
    Poll,
)
from tournesol.models.scaling import ContributorScaling

from .factories.comparison import ComparisonCriteriaScoreFactory, VideoFactory
from .factories.poll import PollWithCriteriasFactory


@override_settings(MEHESTAN_MULTIPROCESSING=False)
class TestMlTrain(TransactionTestCase):
    serialized_rollback = True

    def setUp(self) -> None:
        EmailDomain.objects.create(
            domain="@verified.test", status=EmailDomain.STATUS_ACCEPTED
        )

    def test_ml_train(self):
        user1 = UserFactory(email="user1@verified.test")

        # Create 10 comparisons on 20 distinct videos
        ComparisonCriteriaScoreFactory.create_batch(
            10,
            comparison__user=user1,
        )

        self.assertEqual(EntityCriteriaScore.objects.count(), 0)
        self.assertEqual(ContributorRatingCriteriaScore.objects.count(), 0)
        call_command("ml_train")
        self.assertEqual(
            EntityCriteriaScore.objects.filter(score_mode="default").count(), 20
        )
        self.assertEqual(ContributorRatingCriteriaScore.objects.count(), 20)
        # Asserts that all contributors have been assigned a strictly positive voting right
        self.assertEqual(
            ContributorRatingCriteriaScore.objects.filter(voting_right__gt=0.0).count(),
            20,
        )

    def test_tournesol_score_are_computed(self):
        """
        The ML train should update the tournesol score of each `Entity` and
        `EntityPollRating`.
        """
        default_poll = Poll.default_poll()
        user1 = UserFactory(email="user1@verified.test")
        user2 = UserFactory(email="user2@verified.test")

        video1 = VideoFactory(make_safe_for_poll=False)
        video2 = VideoFactory(make_safe_for_poll=False)
        rating_1 = EntityPollRating.objects.create(entity=video1, poll=default_poll)
        rating_2 = EntityPollRating.objects.create(entity=video2, poll=default_poll)

        for user in [user1, user2]:
            ComparisonCriteriaScoreFactory(
                comparison__user=user,
                comparison__entity_1=video1,
                comparison__entity_2=video2,
                score=10,
                criteria="largely_recommended",
            )

        self.assertEqual(rating_1.tournesol_score, None)
        self.assertEqual(rating_2.tournesol_score, None)

        call_command("ml_train")
        rating_1.refresh_from_db()
        rating_2.refresh_from_db()
        self.assertTrue(rating_1.tournesol_score < 0)
        self.assertTrue(rating_2.tournesol_score > 0)

    def test_ml_on_multiple_polls(self):
        user1 = UserFactory(email="user1@verified.test")
        poll2 = PollWithCriteriasFactory.create()

        # Create 4 comparisons on 8 distinct entitites on the default poll
        ComparisonCriteriaScoreFactory.create_batch(
            4, comparison__user=user1, comparison__poll=Poll.default_poll()
        )

        # Create 10 comparisons on 20 distinct videos in the custom poll
        ComparisonCriteriaScoreFactory.create_batch(
            10, comparison__user=user1, comparison__poll=poll2
        )

        self.assertEqual(EntityCriteriaScore.objects.count(), 0)
        self.assertEqual(len(poll2.criterias_list), 1)

        call_command("ml_train")

        scores_mode_default = EntityCriteriaScore.objects.filter(score_mode="default")
        self.assertEqual(scores_mode_default.count(), 28)
        self.assertEqual(scores_mode_default.filter(poll=poll2).count(), 20)
        self.assertEqual(
            scores_mode_default.filter(poll=Poll.default_poll()).count(), 8
        )

    def test_ml_run_with_video_having_score_zero(self):
        video = VideoFactory(make_safe_for_poll=False)
        ComparisonCriteriaScoreFactory(
            comparison__entity_1=video,
            score=0,
            criteria="largely_recommended",
        )
        rating = video.all_poll_ratings.get()

        self.assertEqual(rating.tournesol_score, None)
        call_command("ml_train")
        rating.refresh_from_db()
        self.assertAlmostEqual(rating.tournesol_score, 0.0, delta=3)

    def test_individual_scaling_are_computed(self):
        # User 1 will belong to calibration users (as the most active trusted user)
        user1 = UserFactory(email="user@verified.test")
        user2 = UserFactory()

        for user in [user1, user2]:
            ComparisonCriteriaScoreFactory.create_batch(
                10, comparison__user=user, criteria="largely_recommended"
            )

        self.assertEqual(EntityCriteriaScore.objects.count(), 0)
        self.assertEqual(ContributorRatingCriteriaScore.objects.count(), 0)
        self.assertEqual(ContributorScaling.objects.count(), 0)

        call_command("ml_train")

        self.assertEqual(ContributorRatingCriteriaScore.objects.count(), 40)
        self.assertEqual(ContributorScaling.objects.count(), 2)

        # Check scaling values for user1
        calibration_scaling = ContributorScaling.objects.get(user=user1)
        self.assertAlmostEqual(calibration_scaling.scale, 1.0)
        self.assertAlmostEqual(calibration_scaling.translation, 0.0)
        # Scaling uncertainties are also defined for scaling calibration users
        self.assertAlmostEqual(calibration_scaling.scale_uncertainty, 1.0)
        self.assertAlmostEqual(calibration_scaling.translation_uncertainty, 1.0)

        # Check scaling values for user2
        scaling = ContributorScaling.objects.get(user=user2)
        self.assertAlmostEqual(scaling.scale, 1.0)
        self.assertAlmostEqual(scaling.translation, 0.0)
        self.assertAlmostEqual(scaling.scale_uncertainty, 1.0)
        self.assertAlmostEqual(scaling.translation_uncertainty, 1.0)

    def test_tournesol_scores_different_trust(self):
        # 10 pretrusted users
        verified_users = [
            UserFactory(email=f"user_{n}@verified.test") for n in range(10)
        ]

        # 20 non_verified_users
        non_verified_users = UserFactory.create_batch(20)

        video1 = VideoFactory(make_safe_for_poll=False)
        video2 = VideoFactory(make_safe_for_poll=False)

        # Pretrusted users prefer video 2
        for user in verified_users:
            ComparisonCriteriaScoreFactory(
                comparison__user=user,
                comparison__entity_1=video1,
                comparison__entity_2=video2,
                score=10,
                criteria="largely_recommended",
            )

        # Other users prefer video 1
        for user in non_verified_users:
            ComparisonCriteriaScoreFactory(
                comparison__user=user,
                comparison__entity_1=video1,
                comparison__entity_2=video2,
                score=-10,
                criteria="largely_recommended",
            )

        rating1 = video1.all_poll_ratings.get()
        rating2 = video2.all_poll_ratings.get()

        self.assertEqual(rating1.tournesol_score, None)
        self.assertEqual(rating2.tournesol_score, None)
        call_command("ml_train")
        rating1.refresh_from_db()
        rating2.refresh_from_db()
        # At least 1 pt difference between the 2 videos
        self.assertGreater(rating2.tournesol_score, rating1.tournesol_score + 1)

        # Asserts that voting rights have been given the correct values based on the number of
        # contributors and their verified status
        # 0.4 = 0.8 [verified] * 0.5 [privacy penalty]
        # 0.12 ~= (2 [non trusted bias] + 0.1 [non trusted scale] * 10 [num trusted] * 0.8 * 0.5 [privacy penalty]) / 20 [num non trusted]
        self.assertEqual(
            ContributorRatingCriteriaScore.objects.get(
                contributor_rating__user=verified_users[0],
                contributor_rating__entity=video2,
            ).voting_right,
            0.4,
        )
        self.assertAlmostEqual(
            ContributorRatingCriteriaScore.objects.get(
                contributor_rating__user=non_verified_users[0],
                contributor_rating__entity=video2,
            ).voting_right,
            0.12,
            places=3,
        )

    def test_tournesol_scores_different_privacy_status(self):
        user1 = UserFactory()
        user2 = UserFactory()

        video1 = VideoFactory(make_safe_for_poll=False)
        video2 = VideoFactory(make_safe_for_poll=False)

        # User1 prefers video1, and their ratings are public
        ComparisonCriteriaScoreFactory(
            comparison__user=user1,
            comparison__entity_1=video1,
            comparison__entity_2=video2,
            score=-10,
            criteria="largely_recommended",
        )
        ContributorRating.objects.filter(user=user1).update(is_public=True)

        # User2 prefers video2, and their ratings are private
        ComparisonCriteriaScoreFactory(
            comparison__user=user2,
            comparison__entity_1=video1,
            comparison__entity_2=video2,
            score=10,
            criteria="largely_recommended",
        )
        ContributorRating.objects.filter(user=user2).update(is_public=False)

        rating1 = video1.all_poll_ratings.get()
        rating2 = video2.all_poll_ratings.get()

        self.assertEqual(rating1.tournesol_score, None)
        self.assertEqual(rating2.tournesol_score, None)
        call_command("ml_train")
        rating1.refresh_from_db()
        rating2.refresh_from_db()

        self.assertGreater(rating1.tournesol_score, rating2.tournesol_score + 1)
