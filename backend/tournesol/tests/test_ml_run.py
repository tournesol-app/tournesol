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
from django.test import TransactionTestCase

from core.models import EmailDomain
from core.tests.factories.user import UserFactory
from tournesol.models import (
    ContributorRating,
    ContributorRatingCriteriaScore,
    EntityCriteriaScore,
    Poll,
)
from tournesol.models.scaling import ContributorScaling

from .factories.comparison import ComparisonCriteriaScoreFactory, VideoFactory
from .factories.poll import PollWithCriteriasFactory


class TestMlTrain(TransactionTestCase):
    serialized_rollback = True

    def setUp(self) -> None:
        EmailDomain.objects.create(domain="@verified.test", status=EmailDomain.STATUS_ACCEPTED)


    def test_ml_train(self):
        user1 = UserFactory(email="user1@verified.test")

        # Create 10 comparisons on 20 distinct videos
        ComparisonCriteriaScoreFactory.create_batch(
            10, comparison__user=user1,
        )

        self.assertEqual(EntityCriteriaScore.objects.count(), 0)
        self.assertEqual(ContributorRatingCriteriaScore.objects.count(), 0)
        call_command("ml_train")
        self.assertEqual(EntityCriteriaScore.objects.filter(score_mode="default").count(), 20)
        self.assertEqual(ContributorRatingCriteriaScore.objects.count(), 20)
        # Asserts that all contributors have been assigned a strictly positive voting right
        self.assertEqual(ContributorRatingCriteriaScore.objects.filter(voting_right__gt=0.).count(), 20)


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
        self.assertEqual(scores_mode_default.filter(poll=Poll.default_poll()).count(), 8)


    def test_ml_run_with_video_having_score_zero(self):
        video = VideoFactory()
        ComparisonCriteriaScoreFactory(
            comparison__entity_1=video,
            score=0,
            criteria="largely_recommended",
        )

        self.assertEqual(video.tournesol_score, None)
        call_command("ml_train")
        video.refresh_from_db()
        self.assertAlmostEqual(video.tournesol_score, 0.0)


    def test_individual_scaling_are_computed(self):
        # User 1 will belong to calibration users (as the most active trusted user)
        user1 = UserFactory(email="user@verified.test")
        user2 = UserFactory()

        for user in [user1, user2]:
            ComparisonCriteriaScoreFactory.create_batch(
                10,
                comparison__user=user,
                criteria="largely_recommended"
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
            UserFactory(email=f"user_{n}@verified.test")
            for n in range(10)
        ]

        # 20 non_verified_users
        non_verified_users = UserFactory.create_batch(20)

        video1 = VideoFactory()
        video2 = VideoFactory()

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

        self.assertEqual(video1.tournesol_score, None)
        self.assertEqual(video2.tournesol_score, None)
        call_command("ml_train")
        video1.refresh_from_db()
        video2.refresh_from_db()
        self.assertAlmostEqual(video1.tournesol_score, -44.0, places=1)
        self.assertAlmostEqual(video2.tournesol_score, 44.0, places=1)
        # Asserts that voting rights have been given the correct values based on the number of
        # contributors and their verified status
        # 0.4 = 0.8 [verified] * 0.5 [privacy penalty]
        # 0.12 ~= (2 [non trusted bias] + 0.1 [non trusted scale] * 10 [num trusted] * 0.8 * 0.5 [privacy penalty]) / 20 [num non trusted]
        self.assertEqual(ContributorRatingCriteriaScore.objects.get(contributor_rating__user=verified_users[0], contributor_rating__entity=video2).voting_right, 0.4)
        self.assertAlmostEqual(ContributorRatingCriteriaScore.objects.get(contributor_rating__user=non_verified_users[0], contributor_rating__entity=video2).voting_right, 0.12, places=3)


    def test_tournesol_scores_different_uncertainty(self):
        user1 = UserFactory()
        user2 = UserFactory()

        video1 = VideoFactory()
        video2 = VideoFactory()

        # User1 prefers video1
        ComparisonCriteriaScoreFactory(
            comparison__user=user1,
            comparison__entity_1=video1,
            comparison__entity_2=video2,
            score=-10,
            criteria="largely_recommended",
        )

        # User2 prefers video2
        ComparisonCriteriaScoreFactory(
            comparison__user=user2,
            comparison__entity_1=video1,
            comparison__entity_2=video2,
            score=10,
            criteria="largely_recommended",
        )

        # Reduce uncertainty on user1 scores by creating additional comparisons
        additional_videos = VideoFactory.create_batch(6)
        for (vid_a, vid_b) in zip(additional_videos, additional_videos[1:]):
            ComparisonCriteriaScoreFactory(
                comparison__entity_1=vid_a,
                comparison__entity_2=vid_b,
                comparison__user=user1,
                score=1,
                criteria="largely_recommended",
            )

        self.assertEqual(video1.tournesol_score, None)
        self.assertEqual(video2.tournesol_score, None)
        call_command("ml_train")
        video1.refresh_from_db()
        video2.refresh_from_db()

        self.assertAlmostEqual(video1.tournesol_score, 8.8, places=1)
        self.assertAlmostEqual(video2.tournesol_score, -8.8, places=1)


    def test_tournesol_scores_different_privacy_status(self):
        user1 = UserFactory()
        user2 = UserFactory()

        video1 = VideoFactory()
        video2 = VideoFactory()

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


        self.assertEqual(video1.tournesol_score, None)
        self.assertEqual(video2.tournesol_score, None)
        call_command("ml_train")
        video1.refresh_from_db()
        video2.refresh_from_db()

        self.assertAlmostEqual(video1.tournesol_score, 44.0, places=1)
        self.assertAlmostEqual(video2.tournesol_score, -44.0, places=1)
