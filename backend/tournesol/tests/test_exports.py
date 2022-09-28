import csv
import io

from django.core.cache import cache
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from core.models import User
from core.tests.factories.user import UserFactory
from tournesol.models import ComparisonCriteriaScore, ContributorRating, Poll
from tournesol.tests.factories.comparison import ComparisonCriteriaScoreFactory, ComparisonFactory
from tournesol.tests.factories.entity import VideoFactory


class ExportTest(TestCase):
    def setUp(self) -> None:
        self.poll_videos = Poll.default_poll()
        self.user_with_comparisons = User.objects.create_user(
            username="user_with", email="user_with@example.com"
        )

        self.video1 = VideoFactory()
        self.video2 = VideoFactory()
        self.comparison = ComparisonFactory(
            user=self.user_with_comparisons,
            entity_1=self.video1,
            entity_2=self.video2,
        )
        ComparisonCriteriaScore.objects.create(
            comparison=self.comparison, score=5, criteria="largely_recommended"
        )
        self.user_without_comparisons = UserFactory()

        self.public_comparisons = UserFactory()
        self.video_public_1 = VideoFactory()
        self.video_public_2 = VideoFactory()
        self.video_private_3 = VideoFactory()
        ContributorRating.objects.create(
            poll=self.poll_videos,
            user=self.public_comparisons,
            entity=self.video_public_1,
            is_public=True,
        )
        ContributorRating.objects.create(
            poll=self.poll_videos,
            user=self.public_comparisons,
            entity=self.video_public_2,
            is_public=True,
        )
        ContributorRating.objects.create(
            poll=self.poll_videos,
            user=self.public_comparisons,
            entity=self.video_private_3,
            is_public=False,
        )
        self.comparison_public = ComparisonFactory(
            poll=self.poll_videos,
            user=self.public_comparisons,
            entity_1=self.video_public_1,
            entity_2=self.video_public_2,
        )
        ComparisonCriteriaScoreFactory(
            comparison=self.comparison_public, score=5, criteria="largely_recommended"
        )
        self.comparison_private = ComparisonFactory(
            user=self.public_comparisons,
            entity_1=self.video_public_1,
            entity_2=self.video_private_3,
        )
        ComparisonCriteriaScoreFactory(
            comparison=self.comparison_private, score=5, criteria="largely_recommended"
        )

        self.client = APIClient()
        cache.clear()

    def test_not_authenticated_cannot_download_comparisons(self):
        resp = self.client.get("/users/me/exports/comparisons/")
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_with_comparisons_can_download_comparisons(self):
        self.client.force_authenticate(self.user_with_comparisons)
        resp = self.client.get("/users/me/exports/comparisons/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # Ensures that the csv contians a single row with the correct score
        csv_file = csv.DictReader(io.StringIO(resp.content.decode()))
        comparison_list = [row for row in csv_file]
        self.assertEqual(len(comparison_list), 1)
        self.assertEqual(float(comparison_list[0]["score"]), 5.0)

    def test_authenticated_without_comparisons_can_download_comparisons(self):
        self.client.force_authenticate(self.user_without_comparisons)
        resp = self.client.get("/users/me/exports/comparisons/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # Ensures the csv does not contain information about comparison criteria score
        csv_file = csv.DictReader(io.StringIO(resp.content.decode()))
        comparison_list = [row for row in csv_file]
        self.assertEqual(len(comparison_list), 0)

    def test_not_authenticated_cannot_download_all(self):
        resp = self.client.get("/users/me/exports/all/")
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_with_comparisons_can_download_all(self):
        self.client.force_authenticate(self.user_with_comparisons)
        resp = self.client.get("/users/me/exports/all/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.headers["Content-Type"], "application/zip")

    def test_authenticated_without_comparisons_can_download_all(self):
        self.client.force_authenticate(self.user_without_comparisons)
        resp = self.client.get("/users/me/exports/all/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.headers["Content-Type"], "application/zip")

    def test_not_authenticated_can_download_public_comparisons(self):
        resp = self.client.get("/exports/comparisons/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # Ensures the csv does not contain information that are not public comparisons
        csv_file = csv.DictReader(io.StringIO(resp.content.decode()))
        comparison_list = [row for row in csv_file]
        self.assertEqual(len(comparison_list), 1)
        self.assertEqual(comparison_list[0]["video_a"], self.video_public_1.video_id)
        self.assertEqual(comparison_list[0]["video_b"], self.video_public_2.video_id)

    def test_not_authenticated_can_download_public_comparisons_multiple_users(self):
        self.public_comparisons2 = UserFactory()
        self.video_public_3 = VideoFactory()
        self.video_public_4 = VideoFactory()
        ContributorRating.objects.create(
            poll=self.poll_videos,
            user=self.public_comparisons2,
            entity=self.video_public_3,
            is_public=True,
        )
        ContributorRating.objects.create(
            poll=self.poll_videos,
            user=self.public_comparisons2,
            entity=self.video_public_4,
            is_public=True,
        )
        self.comparison_public2 = ComparisonFactory(
            user=self.public_comparisons2,
            entity_1=self.video_public_3,
            entity_2=self.video_public_4,
        )
        ComparisonCriteriaScoreFactory(
            comparison=self.comparison_public2, score=10, criteria="largely_recommended"
        )
        resp = self.client.get("/exports/comparisons/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # Ensures the csv does not contain information that are not public comparisons
        csv_file = csv.DictReader(io.StringIO(resp.content.decode()))
        comparison_list = [row for row in csv_file]
        self.assertEqual(len(comparison_list), 2)
        self.assertEqual(comparison_list[0]["video_a"], self.video_public_1.video_id)
        self.assertEqual(comparison_list[0]["video_b"], self.video_public_2.video_id)
        self.assertEqual(comparison_list[1]["video_a"], self.video_public_3.video_id)
        self.assertEqual(comparison_list[1]["video_b"], self.video_public_4.video_id)
