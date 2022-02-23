from django.core.management import call_command
from django.test import TestCase

from core.models import EmailDomain
from core.tests.factories.user import UserFactory
from tournesol.models import ContributorRatingCriteriaScore, EntityCriteriaScore

from .factories.comparison import ComparisonCriteriaScoreFactory, VideoFactory


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
        user1 = UserFactory(email="user1@verified.test")
        user2 = UserFactory(email="user2@verified.test")

        self.video1 = VideoFactory()
        self.video2 = VideoFactory()

        ComparisonCriteriaScoreFactory(comparison__user=user1, comparison__entity_1=self.video1, comparison__entity_2=self.video2, score=10)
        ComparisonCriteriaScoreFactory(comparison__user=user2, comparison__entity_1=self.video1, comparison__entity_2=self.video2, score=10)

        not_trusted_user1 = UserFactory(email="not_trusted_user1@not_verified.test")
        not_trusted_user2 = UserFactory(email="not_trusted_user2@not_verified.test")
        not_trusted_user3 = UserFactory(email="not_trusted_user3@not_verified.test")
        not_trusted_user4 = UserFactory(email="not_trusted_user4@not_verified.test")
        not_trusted_user5 = UserFactory(email="not_trusted_user5@not_verified.test")
        not_trusted_user6 = UserFactory(email="not_trusted_user6@not_verified.test")
        not_trusted_user7 = UserFactory(email="not_trusted_user7@not_verified.test")
        not_trusted_user8 = UserFactory(email="not_trusted_user8@not_verified.test")
        not_trusted_user9 = UserFactory(email="not_trusted_user9@not_verified.test")
        not_trusted_user10 = UserFactory(email="not_trusted_user10@not_verified.test")

        ComparisonCriteriaScoreFactory(comparison__user=not_trusted_user1, comparison__entity_1=self.video1, comparison__entity_2=self.video2, score=-10)
        ComparisonCriteriaScoreFactory(comparison__user=not_trusted_user2, comparison__entity_1=self.video1, comparison__entity_2=self.video2, score=-10)
        ComparisonCriteriaScoreFactory(comparison__user=not_trusted_user3, comparison__entity_1=self.video1, comparison__entity_2=self.video2, score=-10)
        ComparisonCriteriaScoreFactory(comparison__user=not_trusted_user4, comparison__entity_1=self.video1, comparison__entity_2=self.video2, score=-10)
        ComparisonCriteriaScoreFactory(comparison__user=not_trusted_user5, comparison__entity_1=self.video1, comparison__entity_2=self.video2, score=-10)
        ComparisonCriteriaScoreFactory(comparison__user=not_trusted_user6, comparison__entity_1=self.video1, comparison__entity_2=self.video2, score=-10)
        ComparisonCriteriaScoreFactory(comparison__user=not_trusted_user7, comparison__entity_1=self.video1, comparison__entity_2=self.video2, score=-10)
        ComparisonCriteriaScoreFactory(comparison__user=not_trusted_user8, comparison__entity_1=self.video1, comparison__entity_2=self.video2, score=-10)
        ComparisonCriteriaScoreFactory(comparison__user=not_trusted_user9, comparison__entity_1=self.video1, comparison__entity_2=self.video2, score=-10)
        ComparisonCriteriaScoreFactory(comparison__user=not_trusted_user10, comparison__entity_1=self.video1, comparison__entity_2=self.video2, score=-10)

    def test_ml_train(self):
        self.assertEqual(EntityCriteriaScore.objects.count(), 0)
        self.assertEqual(ContributorRatingCriteriaScore.objects.count(), 0)
        call_command("ml_train")
        self.assertEqual(EntityCriteriaScore.objects.count(), 2)
        self.assertEqual(ContributorRatingCriteriaScore.objects.count(), 24)
        self.assertLess(EntityCriteriaScore.objects.get(entity_id=self.video1.id).score, 0)
        self.assertGreater(EntityCriteriaScore.objects.get(entity_id=self.video2.id).score, 0)