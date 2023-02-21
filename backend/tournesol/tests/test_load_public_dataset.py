import tempfile

from django.core.management import call_command
from django.test import TransactionTestCase, override_settings
from rest_framework.test import APIClient

from core.models import User
from core.utils.time import time_ago
from tournesol.entities.video import TYPE_VIDEO
from tournesol.models import Comparison, ContributorRating, Entity
from tournesol.tests.factories.comparison import ComparisonCriteriaScoreFactory
from tournesol.tests.utils.mock_now import MockNow


class TestLoadPublicDataset(TransactionTestCase):
    serialized_rollback = True

    def setUp(self):
        self.client = APIClient()

        with MockNow.Context(time_ago(days=1)):
            ComparisonCriteriaScoreFactory()
            ContributorRating.objects.update(is_public=True)

        public_comparisons_resp = self.client.get("/exports/comparisons/")
        with tempfile.NamedTemporaryFile(mode="wb", delete=False) as comparisons_file:
            comparisons_file.write(public_comparisons_resp.content)
            self.comparisons_path = comparisons_file.name

        User.objects.all().delete()
        Entity.objects.filter(type=TYPE_VIDEO).delete()

    @override_settings(YOUTUBE_API_KEY=None)
    def test_load_public_dataset(self):
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(Comparison.objects.count(), 0)
        self.assertEqual(Entity.objects.filter(type=TYPE_VIDEO).count(), 0)

        call_command("load_public_dataset", "--comparisons-url", self.comparisons_path)

        self.assertEqual(User.objects.count(), 2)  # 1 user from public dataset + 1 test user
        self.assertEqual(Comparison.objects.count(), 1)
        self.assertEqual(Entity.objects.filter(type=TYPE_VIDEO).count(), 2)
