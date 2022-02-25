from django.core.management import call_command
from django.test import TestCase

from core.models import EmailDomain
from core.tests.factories.user import UserFactory
from tournesol.models import ComparisonCriteriaScore, EntityCriteriaScore, Poll

from .factories.comparison import ComparisonCriteriaScoreFactory
from .factories.poll import PollWithCriterasFactory


class TestMlTrain(TestCase):
    def setUp(self) -> None:
        EmailDomain.objects.create(
            domain="@verified.test",
            status=EmailDomain.STATUS_ACCEPTED
        )

        self.poll = PollWithCriterasFactory.create()

        user = UserFactory(email="user@verified.test")
        # Comparison on default poll
        ComparisonCriteriaScoreFactory.create_batch(10, comparison__user=user)
        # Comparison on custom poll
        ComparisonCriteriaScoreFactory.create_batch(10, comparison__user=user, comparison__poll=self.poll)

        
            
    def test_ml_on_multiple_poll(self):

        self.assertEqual(EntityCriteriaScore.objects.count(), 0)
        self.assertEqual(ComparisonCriteriaScore.objects.exclude(comparison__poll=self.poll).count(),10)
        self.assertEqual(ComparisonCriteriaScore.objects.filter(comparison__poll=self.poll).count(),10)
        self.assertEqual(len(self.poll.criterias_list),1)

        call_command("ml_train")

        self.assertEqual(EntityCriteriaScore.objects.count(), 40)
        self.assertEqual(EntityCriteriaScore.objects.filter(poll=self.poll).count(),20)
        self.assertEqual(EntityCriteriaScore.objects.filter(poll=Poll.default_poll()).count(),20)