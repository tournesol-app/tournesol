import tempfile

from django.core.management import call_command
from django.test import TransactionTestCase, override_settings
from rest_framework.test import APIClient

from core.models import User
from core.tests.factories.user import UserFactory
from core.utils.time import time_ago
from tournesol.entities.video import TYPE_VIDEO
from tournesol.models import Comparison, ContributorRating, Entity
from tournesol.tests.factories.comparison import ComparisonCriteriaScoreFactory
from tournesol.tests.utils.mock_now import MockNow


class TestLoadPublicDataset(TransactionTestCase):
    serialized_rollback = True

    @override_settings(MEDIA_ROOT=tempfile.mkdtemp(prefix="TestLoadPublicDataset"))
    def setUp(self):
        self.client = APIClient()

        with MockNow.Context(time_ago(days=8)):
            user = UserFactory(username="public_user", trust_score=0.9123)
            ComparisonCriteriaScoreFactory(comparison__user=user)
            ContributorRating.objects.update(is_public=True)

        call_command("create_dataset")
        public_dataset_resp = self.client.get("/exports/all/")
        with tempfile.NamedTemporaryFile(mode="wb", delete=False) as dataset_file:
            dataset_file.write(public_dataset_resp.content)
            self.comparisons_path = dataset_file.name

        User.objects.all().delete()
        Entity.objects.filter(type=TYPE_VIDEO).delete()

    @override_settings(YOUTUBE_API_KEY=None)
    def test_load_public_dataset(self):
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(Comparison.objects.count(), 0)
        self.assertEqual(Entity.objects.filter(type=TYPE_VIDEO).count(), 0)

        call_command("load_public_dataset", "--dataset-url", self.comparisons_path)

        self.assertEqual(User.objects.count(), 2)  # 1 user from public dataset + 1 test user
        public_user = User.objects.get(username="public_user")
        self.assertTrue(public_user.has_trusted_email)
        # Trust score is rounded to 2 decimals in public dataset
        self.assertAlmostEqual(public_user.trust_score, 0.91)

        self.assertEqual(Comparison.objects.count(), 1)
        self.assertEqual(Entity.objects.filter(type=TYPE_VIDEO).count(), 2)
