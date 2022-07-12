from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from core.tests.factories.user import UserFactory
from tournesol.models.poll import Poll
from tournesol.tests.factories.comparison import ComparisonFactory
from tournesol.tests.factories.entity import VideoFactory


class SingleGraphAllConnectedToAllTestCase(TestCase):
    """
    A test case of the unconnected entities API.

    Here, all entities are connected with each other by the tested user,
    forming a single graph.
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

    def test_anon_get_401(self):
        """
        An anonymous user must not be able to list its unconnected entities.
        """
        response = self.client.get(
            f"{self.user_base_url}/{self.video_source.uid}/",
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_auth_get_404_with_no_uid(self):
        self.client.force_authenticate(self.user_1)

        response = self.client.get(
            f"{self.user_base_url}/",
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_auth_get_404_with_unknown_uid(self):
        self.client.force_authenticate(self.user_1)

        response = self.client.get(
            f"{self.user_base_url}/123456788/",
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_auth_get_empty_when_all_entities_are_connected(self):
        self.client.force_authenticate(self.user_1)

        response = self.client.get(
            f"{self.user_base_url}/{self.video_source.uid}/",
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)

        # Make sure that no side-effect affects subsequent requests.
        response = self.client.get(
            f"{self.user_base_url}/{self.video_source.uid}/",
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)


class SingleGraphOneIsolatedEntityTestCase(TestCase):
    """
    A test case of the unconnected entities API.

    Here, there is an entity that doesn't have any comparison with the tested
    user's graph.
    """

    def setUp(self):
        self.client = APIClient()
        self.user_1 = UserFactory()
        self.poll_videos = Poll.default_poll()
        self.user_base_url = f"/users/me/unconnected_entities/{self.poll_videos.name}"

        # Create video without comparison.
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


class SingleGraphAllConnectedTestCase(TestCase):
    """
    A test case of the unconnected entities API.

    Here, all entities are not necessarily connected together to by the tested
    user, yet forming a single graph.
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
        """
        An authenticated user must get an empty list, when all of its compared
        entities are connected, even if they are not individually connected to
        each other.
        """
        self.client.force_authenticate(self.user_1)

        response = self.client.get(
            f"{self.user_base_url}/{self.video_source.uid}/",
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)


class TwoIsolatedGraphsTestCase(TestCase):
    """
    A test case of the unconnected entities API.

    Here, we test two graphs of connected entities that have no connection
    with each other.
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
