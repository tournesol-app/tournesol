from django.core.management import call_command
from django.test import TestCase, TransactionTestCase

from core.models import EmailDomain
from core.tests.factories.user import UserFactory
from tournesol.models import (
    ComparisonCriteriaScore,
    ContributorRating,
    ContributorRatingCriteriaScore,
    EntityCriteriaScore,
    Poll,
)
from tournesol.models.scaling import ContributorScaling

from .factories.comparison import ComparisonCriteriaScoreFactory, VideoFactory
from .factories.poll import PollWithCriteriasFactory


class TestMlTrain(TestCase):
    def setUp(self) -> None:
        EmailDomain.objects.create(
            domain="@verified.test",
            status=EmailDomain.STATUS_ACCEPTED
        )
        EmailDomain.objects.create(
            domain="@not_verified.test",
            status=EmailDomain.STATUS_REJECTED
        )
        self.user1 = UserFactory(email="user1@verified.test")
        self.user2 = UserFactory(email="user2@verified.test")

        self.video1 = VideoFactory()
        self.video2 = VideoFactory()

        self.poll = PollWithCriteriasFactory.create()

        # Comparison on custom poll
        ComparisonCriteriaScoreFactory.create_batch(10, comparison__user=self.user1, comparison__poll=self.poll)

        # Comparison on default poll
        ComparisonCriteriaScoreFactory(comparison__user=self.user1, comparison__entity_1=self.video1, comparison__entity_2=self.video2, score=10)
        ComparisonCriteriaScoreFactory(comparison__user=self.user2, comparison__entity_1=self.video1, comparison__entity_2=self.video2, score=10)

        for i in range(10):
            not_trusted_user = UserFactory(email=f"not_trusted_user{i}@not_verified.test")
            ComparisonCriteriaScoreFactory(
                comparison__user=not_trusted_user,
                comparison__entity_1=self.video1,
                comparison__entity_2=self.video2,
                score=-10
            )

    def test_ml_train(self):
        self.assertEqual(EntityCriteriaScore.objects.count(), 0)
        self.assertEqual(ContributorRatingCriteriaScore.objects.count(), 0)
        call_command("ml_train")
        self.assertEqual(EntityCriteriaScore.objects.count(), 22)
        self.assertEqual(ContributorRatingCriteriaScore.objects.count(), 44)

    def test_ml_on_multiple_poll(self):

        self.assertEqual(EntityCriteriaScore.objects.count(), 0)
        self.assertEqual(ComparisonCriteriaScore.objects.exclude(comparison__poll=self.poll).count(),12)
        self.assertEqual(ComparisonCriteriaScore.objects.filter(comparison__poll=self.poll).count(),10)
        self.assertEqual(len(self.poll.criterias_list),1)

        call_command("ml_train")

        self.assertEqual(EntityCriteriaScore.objects.count(), 22)
        self.assertEqual(EntityCriteriaScore.objects.filter(poll=self.poll).count(),20)
        self.assertEqual(EntityCriteriaScore.objects.filter(poll=Poll.default_poll()).count(),2)


    def test_ml_train_skip_untrusted(self):
        # Test on trusted users only
        self.assertEqual(EntityCriteriaScore.objects.count(), 0)
        self.assertEqual(ContributorRatingCriteriaScore.objects.count(), 0)

        call_command("ml_train", "--skip-untrusted")

        self.assertEqual(EntityCriteriaScore.objects.count(), 22)
        self.assertEqual(ContributorRatingCriteriaScore.objects.count(), 24)

        contributor_rating_user_1 = ContributorRating.objects.get(user=self.user1, entity=self.video1)
        contributor_rating_user_2 = ContributorRating.objects.get(user=self.user2, entity=self.video1)

        self.assertLess(EntityCriteriaScore.objects.get(entity_id=self.video1.id).score, 0)
        self.assertGreater(EntityCriteriaScore.objects.get(entity_id=self.video2.id).score, 0)

    def test_ml_train_on_trusted_and_all_users(self):
        call_command("ml_train", "--skip-untrusted")

        contributor_rating_user_1 = ContributorRating.objects.get(user=self.user1, entity=self.video1)
        contributor_rating_user_2 = ContributorRating.objects.get(user=self.user2, entity=self.video1)
        contributor_rating_score_user_1 = ContributorRatingCriteriaScore.objects.get(contributor_rating=contributor_rating_user_1).score
        contributor_rating_score_user_2 = ContributorRatingCriteriaScore.objects.get(contributor_rating=contributor_rating_user_2).score

        # Test on all user
        call_command("ml_train")

        # Check if trusted user contribution are not affected
        self.assertEqual(ContributorRatingCriteriaScore.objects.get(contributor_rating=contributor_rating_user_1).score,contributor_rating_score_user_1)
        self.assertEqual(ContributorRatingCriteriaScore.objects.get(contributor_rating=contributor_rating_user_2).score,contributor_rating_score_user_2)


        self.assertEqual(EntityCriteriaScore.objects.count(), 22)
        self.assertEqual(ContributorRatingCriteriaScore.objects.count(), 44)
        self.assertLess(EntityCriteriaScore.objects.get(entity_id=self.video1.id).score, 0)
        self.assertGreater(EntityCriteriaScore.objects.get(entity_id=self.video2.id).score, 0)

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
        self.assertEqual(self.video1.tournesol_score, -4.1)
        self.assertEqual(self.video2.tournesol_score, 4.1)


class TestMlTrainMehestan(TransactionTestCase):
    def setUp(self) -> None:
        self.poll = PollWithCriteriasFactory(algorithm="mehestan")
        self.video1 = VideoFactory()
        self.video2 = VideoFactory()

        EmailDomain.objects.create(
            domain="@verified.test",
            status=EmailDomain.STATUS_ACCEPTED
        )

        # User 1 will belong to supertrusted users (as staff member)
        self.user1 = UserFactory(email="user1@verified.test", is_staff=True)

        ComparisonCriteriaScoreFactory.create_batch(10, comparison__user=self.user1, comparison__poll=self.poll)

        for i in range(10):
            not_trusted_user = UserFactory(email=f"not_trusted_user{i}@not_verified.test")
            ComparisonCriteriaScoreFactory(
                comparison__poll=self.poll,
                comparison__user=not_trusted_user,
                comparison__entity_1=self.video1,
                comparison__entity_2=self.video2,
                score=-10
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
