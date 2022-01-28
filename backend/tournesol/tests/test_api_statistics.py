
from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from core.models import User
from tournesol.tests.factories.comparison import ComparisonFactory
from tournesol.tests.factories.video import VideoFactory

from ..models import Comparison, Video


class StatisticsAPI(TestCase):
    """
    TestCase of the statistics API.
    """

    _list_of_users = []
    _list_of_videos = []
    _list_of_comparisons = []

    def setUp(self):
        user_1 = User.objects.create(username="username", email="user@test")
        user_2 = User.objects.create(
                username="username2",
                email="user2@test",
                date_joined=timezone.now() - timedelta(days=90)
        )
        self._list_of_users = [user_1, user_2]

        video_1 = VideoFactory(
            publication_date=timezone.now() - timedelta(days=5),
            uploader="uploader1",
            rating_n_contributors=2,
        )
        video_2 = VideoFactory(
            publication_date=timezone.now() - timedelta(days=30),
            uploader="uploader2",
            rating_n_contributors=3,
        )
        video_3 = VideoFactory(
            publication_date=timezone.now() - timedelta(days=60),
            uploader="uploader2",
            rating_n_contributors=4,
        )
        self._list_of_videos = [video_1, video_2, video_3]

        comparison_1 = ComparisonFactory(
                user=user_1, video_1=video_1, video_2=video_2,
                duration_ms=102
        )
        comparison_2 = ComparisonFactory(
                user=user_2, video_1=video_1, video_2=video_3,
                duration_ms=104
        )
        comparison_3 = ComparisonFactory(
                user=user_2, video_1=video_2, video_2=video_3,
                duration_ms=302
        )

        Comparison.objects.filter(pk=comparison_1.pk).update(datetime_lastedit=timezone.now() - timedelta(days=5))
        Comparison.objects.filter(pk=comparison_2.pk).update(datetime_lastedit=timezone.now() - timedelta(days=29))
        Comparison.objects.filter(pk=comparison_3.pk).update(datetime_lastedit=timezone.now() - timedelta(days=60))
            
        self._list_of_comparisons = [comparison_1, comparison_2, comparison_3]
       

    def test_video_count_is_right(self):
        """
        Test if the number of video is right
        """

        client = APIClient()

        response = client.get(
            reverse("tournesol:statistics_detail"),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        video_count = response.data["video_count"]
        last_month_video_count = response.data["last_month_video_count"]

        self.assertEqual(video_count, len(self._list_of_videos))
        self.assertEqual(last_month_video_count, 2)

    def test_user_count_is_right(self):
        """
        Test if the number of user is right
        """

        client = APIClient()

        response = client.get(
            reverse("tournesol:statistics_detail"),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        user_count = response.data["user_count"]
        last_month_user_count = response.data["last_month_user_count"]

        self.assertEqual(user_count, len(self._list_of_users))
        self.assertEqual(last_month_user_count, 1)

    def test_video_comparison_is_right(self):
        """
        Test if the number of comparison is right
        """

        client = APIClient()

        response = client.get(
            reverse("tournesol:statistics_detail"),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        comparison_count = response.data["comparison_count"]
        last_month_comparison_count = response.data["last_month_comparison_count"]

        print(self._list_of_comparisons)
        self.assertEqual(comparison_count, len(self._list_of_comparisons))
        self.assertEqual(last_month_comparison_count, 2)
