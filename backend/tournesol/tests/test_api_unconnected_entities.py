from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from core.tests.factories.user import UserFactory
from tournesol.models.poll import Poll
from tournesol.tests.factories.comparison import ComparisonFactory
from tournesol.tests.factories.entity import VideoFactory


class SimpleAllConnectedTest(TestCase):
    """
    TestCase for the unconnected entities API.
    In this simple test, all video are connected to the user.
    """

    def setUp(self):
        self.client = APIClient()
        self.user_1 = UserFactory()
        user_2 = UserFactory()
        self.poll_videos = Poll.default_poll()
        self.user_base_url = f"/users/me/unconnected_entities/{self.poll_videos.name}"

        video_1 = VideoFactory()
        video_2 = VideoFactory()
        video_3 = VideoFactory()
        video_4 = VideoFactory()
        video_5 = VideoFactory()

        self.video_source = video_1

        ComparisonFactory(
            user=self.user_1,
            entity_1=video_1,
            entity_2=video_2,
        )
        ComparisonFactory(
            user=self.user_1,
            entity_1=video_1,
            entity_2=video_3,
        )
        ComparisonFactory(
            user=self.user_1,
            entity_1=video_2,
            entity_2=video_3,
        )
        ComparisonFactory(
            user=user_2,
            entity_1=video_4,
            entity_2=video_5,
        )

    def test_not_authenticated_cannot_show_unconnected_entities(self):
        response = self.client.get(
            f"{self.user_base_url}/{self.video_source.uid}/",
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_without_uid_show_not_found(self):
        self.client.force_authenticate(self.user_1)

        response = self.client.get(
            f"{self.user_base_url}/",
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_with_unknown_uid_show_not_found(self):
        self.client.force_authenticate(self.user_1)

        response = self.client.get(
            f"{self.user_base_url}/123456788/",
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_all_connected_video_shouldnt_return_entities(self):
        self.client.force_authenticate(self.user_1)

        response = self.client.get(
            f"{self.user_base_url}/{self.video_source.uid}/",
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)

        # Make sure that no side-effect affects subsequent requests
        response = self.client.get(
            f"{self.user_base_url}/{self.video_source.uid}/",
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)


class NonConnectedEntityTest(TestCase):
    """
    TestCase for the unconnected entities API where an entity don't have any comparison.
    """

    def setUp(self):
        self.client = APIClient()
        self.user_1 = UserFactory()
        self.poll_videos = Poll.default_poll()
        self.user_base_url = f"/users/me/unconnected_entities/{self.poll_videos.name}"

        # Create video without comparison
        video_1 = VideoFactory()
        video_2 = VideoFactory()
        video_3 = VideoFactory()
        video_4 = VideoFactory()
        VideoFactory()

        self.video_source = video_1

        ComparisonFactory(
            user=self.user_1,
            entity_1=video_2,
            entity_2=video_3,
        )
        ComparisonFactory(
            user=self.user_1,
            entity_1=video_3,
            entity_2=video_4,
        )

    def test_no_link_should_return_all(self):
        self.client.force_authenticate(self.user_1)

        response = self.client.get(
            f"{self.user_base_url}/{self.video_source.uid}/",
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 3)


class AdvancedAllConnectedTest(TestCase):
    """
    TestCase for the unconnected entities API. 
    In this Advanced test, all video are not necessarily connected to the user.
    """

    def setUp(self):
        self.client = APIClient()
        self.user_1 = UserFactory()
        self.poll_videos = Poll.default_poll()
        self.user_base_url = f"/users/me/unconnected_entities/{self.poll_videos.name}"

        video_4 = VideoFactory()
        video_3 = VideoFactory()
        video_2 = VideoFactory()
        video_1 = VideoFactory()

        self.video_source = video_1

        ComparisonFactory(
            user=self.user_1,
            entity_1=video_3,
            entity_2=video_4,
        )
        ComparisonFactory(
            user=self.user_1,
            entity_1=video_2,
            entity_2=video_3,
        )
        ComparisonFactory(
            user=self.user_1,
            entity_1=video_1,
            entity_2=video_3,
        )

    def test_all_linked_should_return_empty(self):
        self.client.force_authenticate(self.user_1)

        response = self.client.get(
            f"{self.user_base_url}/{self.video_source.uid}/",
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)


class SimpleNotAllConnectedTest(TestCase):
    """
    TestCase for the unconnected entities API.
    """

    def setUp(self):
        self.client = APIClient()
        self.user_1 = UserFactory()
        self.poll_videos = Poll.default_poll()
        self.user_base_url = f"/users/me/unconnected_entities/{self.poll_videos.name}"

        video_1 = VideoFactory()
        video_2 = VideoFactory()
        video_3 = VideoFactory()
        video_4 = VideoFactory()
        video_5 = VideoFactory()

        self.unrelated_video = [video_4, video_5]

        self.video_source = video_1

        ComparisonFactory(
            user=self.user_1,
            entity_1=video_1,
            entity_2=video_2,
        )
        ComparisonFactory(
            user=self.user_1,
            entity_1=video_1,
            entity_2=video_3,
        )
        ComparisonFactory(
            user=self.user_1,
            entity_1=video_2,
            entity_2=video_3,
        )
        ComparisonFactory(
            user=self.user_1,
            entity_1=video_4,
            entity_2=video_5,
        )

    def test_should_return_non_connected_entity(self):
        self.client.force_authenticate(self.user_1)

        response = self.client.get(
            f"{self.user_base_url}/{self.video_source.uid}/",
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(
            list(map(lambda x: x["uid"], response.data["results"])),
            list(map(lambda x: x.uid, self.unrelated_video))
        )


class AdvancedNotAllConnectedTest(TestCase):
    """
    TestCase for the unconnected entities API.
    """

    def setUp(self):
        self.client = APIClient()
        self.user_1 = UserFactory()
        user_2 = UserFactory()
        self.poll_videos = Poll.default_poll()
        self.user_base_url = f"/users/me/unconnected_entities/{self.poll_videos.name}"

        video_1 = VideoFactory()
        video_2 = VideoFactory()
        video_3 = VideoFactory()
        video_4 = VideoFactory()
        video_5 = VideoFactory()
        video_6 = VideoFactory()
        video_7 = VideoFactory()

        self.unrelated_video = [video_6, video_7]

        self.video_source = video_1

        ComparisonFactory(
            user=self.user_1,
            entity_1=video_4,
            entity_2=video_5,
        )
        ComparisonFactory(
            user=self.user_1,
            entity_1=video_2,
            entity_2=video_4,
        )
        ComparisonFactory(
            user=user_2,
            entity_1=video_2,
            entity_2=video_6,
        )
        ComparisonFactory(
            user=self.user_1,
            entity_1=video_7,
            entity_2=video_6,
        )
        ComparisonFactory(
            user=self.user_1,
            entity_1=video_3,
            entity_2=video_2,
        )
        ComparisonFactory(
            user=self.user_1,
            entity_1=video_3,
            entity_2=video_1,
        )

    def test_should_return_non_connected_entity(self):
        self.client.force_authenticate(self.user_1)

        response = self.client.get(
            f"{self.user_base_url}/{self.video_source.uid}/",
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(
            [entity['uid'] for entity in response.data["results"]],
            [entity.uid for entity in self.unrelated_video]
        )
