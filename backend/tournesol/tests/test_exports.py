import csv
import io

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from core.models import User
from tournesol.models import Comparison, Video, ComparisonCriteriaScore

class ExportTest(TestCase):
    def setUp(self) -> None:
        self.user_with_comparisons = User.objects.create_user(username="user_with", email="user_with@example.com")
        
        self.video1 = Video.objects.create(video_id="test_all_data_1", name="test_all_data_1")
        self.video2 = Video.objects.create(video_id="test_all_data_2", name="test_all_data_2")
        self.comparison = Comparison.objects.create(user=self.user_with_comparisons, video_1=self.video1, video_2=self.video2)
        ComparisonCriteriaScore.objects.create(comparison=self.comparison,score=5,criteria="largely_recommended")
        self.user_without_comparisons = User.objects.create_user(username="user_without", email="user_without@example.com")
        self.client = APIClient()

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
        self.assertEqual(float(comparison_list[0]['score']), 5.0)

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

    def test_authenticated_without_comparisons_can_download_all(self):
        self.client.force_authenticate(self.user_without_comparisons)
        resp = self.client.get("/users/me/exports/all/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
