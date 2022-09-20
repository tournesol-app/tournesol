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
For tests that depend on this default Poll, `serialized_rollback = True` to reload the initial state
of the database after each test.

Find more details on https://docs.djangoproject.com/en/4.0/topics/testing/overview/#rollback-emulation
"""

from django.core.management import call_command
from django.test import TransactionTestCase

from core.models import EmailDomain
from core.tests.factories.user import UserFactory
from tournesol.models import (
    ComparisonCriteriaScore,
    ContributorRatingCriteriaScore,
    EntityCriteriaScore,
    Poll,
)
from tournesol.models.poll import ALGORITHM_MEHESTAN
from tournesol.models.scaling import ContributorScaling

from .factories.comparison import ComparisonCriteriaScoreFactory, VideoFactory
from .factories.poll import PollWithCriteriasFactory


class TestMlTrain(TransactionTestCase):
    serialized_rollback = True

    def setUp(self) -> None:
        EmailDomain.objects.create(domain="@verified.test", status=EmailDomain.STATUS_ACCEPTED)
        EmailDomain.objects.create(domain="@not_verified.test", status=EmailDomain.STATUS_REJECTED)
        self.user1 = UserFactory(email="user1@verified.test")
        self.user2 = UserFactory(email="user2@verified.test")

        self.video1 = VideoFactory()
        self.video2 = VideoFactory()

        self.poll = PollWithCriteriasFactory.create()

        # Comparison on custom poll
        ComparisonCriteriaScoreFactory.create_batch(
            10, comparison__user=self.user1, comparison__poll=self.poll
        )

        # Comparison on default poll
        ComparisonCriteriaScoreFactory(
            comparison__user=self.user1,
            comparison__entity_1=self.video1,
            comparison__entity_2=self.video2,
            score=10,
            criteria="largely_recommended",
        )
        ComparisonCriteriaScoreFactory(
            comparison__user=self.user2,
            comparison__entity_1=self.video1,
            comparison__entity_2=self.video2,
            score=10,
            criteria="largely_recommended",
        )   

        for i in range(10):
            # Reduce uncertainty on user1 scores by creating additional comparisons
            ComparisonCriteriaScoreFactory(
                comparison__user=self.user1,
                score=0,
                criteria="largely_recommended",
            )

            # Create comparisons by non-verified users (will be accounted with lower weight by Mehestan)
            not_trusted_user = UserFactory(email=f"not_trusted_user{i}@not_verified.test")
            ComparisonCriteriaScoreFactory(
                comparison__user=not_trusted_user,
                comparison__entity_1=self.video1,
                comparison__entity_2=self.video2,
                score=-10,
                criteria="largely_recommended",
            )


    def test_ml_train(self):
        self.assertEqual(EntityCriteriaScore.objects.count(), 0)
        self.assertEqual(ContributorRatingCriteriaScore.objects.count(), 0)
        call_command("ml_train")
        self.assertEqual(EntityCriteriaScore.objects.filter(score_mode="default").count(), 42)
        self.assertEqual(ContributorRatingCriteriaScore.objects.count(), 64)

    def test_ml_on_multiple_poll(self):
        self.assertEqual(EntityCriteriaScore.objects.count(), 0)
        self.assertEqual(ComparisonCriteriaScore.objects.exclude(comparison__poll=self.poll).count(), 22)
        self.assertEqual(ComparisonCriteriaScore.objects.filter(comparison__poll=self.poll).count(), 10)
        self.assertEqual(len(self.poll.criterias_list), 1)

        call_command("ml_train")

        scores_mode_default = EntityCriteriaScore.objects.filter(score_mode="default")
        self.assertEqual(scores_mode_default.count(), 42)
        self.assertEqual(scores_mode_default.filter(poll=self.poll).count(), 20)
        self.assertEqual(scores_mode_default.filter(poll=Poll.default_poll()).count(), 22)


    def test_tournesol_score_are_computed(self):
        """
        The `tournesol_score` of each entity must be computed during an
        ML train.
        """
        self.assertEqual(self.video1.tournesol_score, None)
        self.assertEqual(self.video2.tournesol_score, None)
        call_command("ml_train")
        self.video1.refresh_from_db()
        self.video2.refresh_from_db()

        self.assertAlmostEqual(self.video1.tournesol_score, -57.4, places=1)
        self.assertAlmostEqual(self.video2.tournesol_score, 57.4, places=1)


class TestMlTrainMehestan(TransactionTestCase):
    def setUp(self) -> None:
        self.poll = PollWithCriteriasFactory(algorithm=ALGORITHM_MEHESTAN)
        self.video1 = VideoFactory()
        self.video2 = VideoFactory()

        EmailDomain.objects.create(domain="@verified.test", status=EmailDomain.STATUS_ACCEPTED)

        # User 1 will belong to supertrusted users (as staff member)
        self.user1 = UserFactory(email="user1@verified.test", is_staff=True)

        ComparisonCriteriaScoreFactory.create_batch(
            10, comparison__user=self.user1, comparison__poll=self.poll
        )

        for i in range(10):
            not_trusted_user = UserFactory(email=f"not_trusted_user{i}@not_verified.test")
            ComparisonCriteriaScoreFactory(
                comparison__poll=self.poll,
                comparison__user=not_trusted_user,
                comparison__entity_1=self.video1,
                comparison__entity_2=self.video2,
                score=-10,
            )

    def test_ml_train(self):
        self.assertEqual(EntityCriteriaScore.objects.count(), 0)
        self.assertEqual(ContributorRatingCriteriaScore.objects.count(), 0)
        self.assertEqual(ContributorScaling.objects.count(), 0)

        call_command("ml_train")

        self.assertEqual(EntityCriteriaScore.objects.filter(score_mode="default").count(), 22)
        self.assertEqual(EntityCriteriaScore.objects.filter(score_mode="all_equal").count(), 22)
        self.assertEqual(EntityCriteriaScore.objects.filter(score_mode="trusted_only").count(), 20)
        self.assertEqual(ContributorRatingCriteriaScore.objects.count(), 40)
        self.assertEqual(ContributorScaling.objects.count(), 11)

        # Check scaling values
        scaling = ContributorScaling.objects.get(user=self.user1)
        self.assertAlmostEqual(scaling.scale, 1.0)
        self.assertAlmostEqual(scaling.translation, 0.0)
        # Scaling uncertainties are not defined for supertrusted users
        self.assertIsNone(scaling.scale_uncertainty)
        self.assertIsNone(scaling.translation_uncertainty)

        # Check tournesol score is saved and scaled correctly
        self.video1.refresh_from_db()
        self.video2.refresh_from_db()
        self.assertGreater(self.video1.tournesol_score, 20)
        self.assertLess(self.video2.tournesol_score, -20)
