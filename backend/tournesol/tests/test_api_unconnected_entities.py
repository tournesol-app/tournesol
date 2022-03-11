from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from core.models import User
from core.tests.factories.user import UserFactory
from tournesol.models.poll import Poll
from tournesol.tests.factories.comparison import ComparisonFactory
from tournesol.tests.factories.entity import VideoFactory


class UnconnectedEntitiesTest(TestCase):
    """
    TestCase for the unconnected entities API.
    """

    def setUp(self):
        self.client = APIClient()
        self.user_1 = UserFactory()
        self.poll_videos = Poll.default_poll()
        self.user_base_url = "/users/me/unconnected_entities/{}".format(
            self.poll_videos.name
        )

        self.video_1 = VideoFactory(
            metadata__uploader="uploader1",
            rating_n_ratings=2,
        )
        video_2 = VideoFactory(
            metadata__uploader="uploader2",
            rating_n_ratings=3,
        )
        video_3 = VideoFactory(
            metadata__uploader="uploader2",
            rating_n_ratings=4,
        )

        comparison_1 = ComparisonFactory(
            user=self.user_1,
            entity_1=self.video_1,
            entity_2=video_2,
            duration_ms=102,
        )
        comparison_2 = ComparisonFactory(
            user=self.user_1,
            entity_1=self.video_1,
            entity_2=video_3,
            duration_ms=104,
        )
        comparison_3 = ComparisonFactory(
            user=self.user_1,
            entity_1=video_2,
            entity_2=video_3,
            duration_ms=302,
        )

    def test_not_authenticated_cannot_show_unconnected_entities(self):
        response = self.client.get(
            "{}/{}/".format(self.user_base_url, self.video_1.id),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_all_connected_video_shouldnt_return_entities(self):
        """
        A connecter user have success result
        """

        self.client.force_authenticate(self.user_1)

        url =  "{}/{}/".format(self.user_base_url, self.video_1.id)
        response = self.client.get(
            url,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)
