
from datetime import datetime, timedelta

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models import User
from tournesol.tests.factories.video import VideoFactory

from ..models import Video


class StatisticsAPI(TestCase):
    """
    TestCase of the statistics API.
    """

    _user = "username"

    _list_of_videos = []

    def setUp(self):
        User.objects.create(username=self._user, email="user@test")

        video_1 = VideoFactory(
            publication_date=datetime.today() - timedelta(days=5),
            uploader="uploader1",
            rating_n_contributors=2,
        )
        video_2 = VideoFactory(
            publication_date=datetime.today() - timedelta(days=30),
            uploader="uploader2",
            rating_n_contributors=3,
        )
        video_3 = VideoFactory(
            publication_date=datetime.today() - timedelta(days=60),
            uploader="uploader2",
            rating_n_contributors=4,
        )
        self._list_of_videos = [video_1, video_2, video_3]

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
