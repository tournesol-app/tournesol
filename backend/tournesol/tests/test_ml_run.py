from django.core.management import call_command
from django.test import TestCase

from core.models import EmailDomain
from core.tests.factories.user import UserFactory
from tournesol.models import EntityCriteriaScore

from .factories.comparison import ComparisonCriteriaScoreFactory


class TestMlTrain(TestCase):
    def setUp(self) -> None:
        EmailDomain.objects.create(
            domain="@verified.test",
            status=EmailDomain.STATUS_ACCEPTED
        )
        user = UserFactory(email="user@verified.test")
        ComparisonCriteriaScoreFactory.create_batch(10, comparison__user=user)
    
    def test_ml_train(self):
        self.assertEqual(EntityCriteriaScore.objects.count(), 0)
        call_command("ml_train")
        self.assertEqual(EntityCriteriaScore.objects.count(), 20)
