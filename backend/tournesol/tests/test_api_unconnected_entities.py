"""
All test cases related to the unconnected entities API.

For a given user, we consider entities and its comparisons as a graph. Entities
are vertices and comparisons edges.

See: https://en.wikipedia.org/wiki/Graph_(discrete_mathematics)
"""

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from core.tests.factories.user import UserFactory
from tournesol.models.poll import Poll
from tournesol.tests.factories.comparison import ComparisonFactory
from tournesol.tests.factories.entity import VideoFactory


class CompleteGraphTestCase(TestCase):
    """
    A test case of the unconnected entities API.

    Here, all entities are connected with each other by the tested user,
    forming a complete graph.

    See: https://en.wikipedia.org/wiki/Complete_graph
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


class IsolatedVertexTestCase(TestCase):
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

    def test_no_link_must_return_all(self):
        self.client.force_authenticate(self.user_1)

        response = self.client.get(
            f"{self.user_base_url}/{self.video_source.uid}/",
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 3)


class ConnectGraphNonReducibleDistanceTestCase(TestCase):
    """
    A test case of the unconnected entities API.

    Here, all entities are not necessarily connected together to by the tested
    user, yet forming a connected graph.

    No entity is distant enough from any other entity to be considered
    connectable.
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

    def test_all_linked_must_return_empty(self):
        """
        An authenticated user must get an empty list, when all of its compared
        entities are connected, and close enough to each other, even if they
        are not individually connected to each other.
        """
        self.client.force_authenticate(self.user_1)

        response = self.client.get(
            f"{self.user_base_url}/{self.video_source.uid}/",
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)


class ConnectedGraphReducibleDistanceTestCase(TestCase):
    """
    A test case of the unconnected entities API.

    Here, all entities are not necessarily connected together to by the tested
    user, yet forming a connected graph.

    Some entities are distant enough from a given entity, that they are considered
    connectable by the API.
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
        # Distant entities.
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

    def test_must_return_non_connected_entities(self):
        self.client.force_authenticate(self.user_1)

        response = self.client.get(
            f"{self.user_base_url}/{self.video_source.uid}/",
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(
            [entity["uid"] for entity in response.data["results"]],
            [entity.uid for entity in self.unrelated_video],
        )

    def test_non_connected_entities_ordering(self):
        """
        The entities returned for an authenticated user, must be ordered by
        their ascending number of comparisons made by this user.
        """
        video_a = VideoFactory()
        video_b = VideoFactory()

        ComparisonFactory(
            user=self.user_1,
            entity_1=video_a,
            entity_2=self.unrelated_video[0],
        )

        ComparisonFactory(
            user=self.user_1,
            entity_1=video_b,
            entity_2=self.unrelated_video[0],
        )

        ComparisonFactory(
            user=self.user_1,
            entity_1=video_b,
            entity_2=self.unrelated_video[1],
        )

        self.client.force_authenticate(self.user_1)
        response = self.client.get(
            f"{self.user_base_url}/{self.video_source.uid}/",
            format="json",
        )

        results = response.data["results"]
        # The first entity must be `video_a`, as it has 1 comparison.
        self.assertEqual(results[0]["uid"], video_a.uid)

        # The 2nd and 3rd entities must be in the list of entities having 2
        # comparisons.
        self.assertIn(results[1]["uid"], [video_b.uid, self.unrelated_video[1].uid])
        self.assertIn(results[2]["uid"], [video_b.uid, self.unrelated_video[1].uid])

        # The fourth entity must be `self.unrelated_video[0]` with 3 comparisons.
        self.assertEqual(results[3]["uid"], self.unrelated_video[0].uid)


class TwoIsolatedGraphComponentsTestCase(TestCase):
    """
    A test case of the unconnected entities API.

    Here, we test two components of connected entities that have no connection
    with each other.
    """

    def setUp(self):
        self.client = APIClient()
        self.user_1 = UserFactory()
        self.poll_videos = Poll.default_poll()
        self.user_base_url = f"/users/me/unconnected_entities/{self.poll_videos.name}"

        # First component of the graph.
        video_1 = VideoFactory()
        video_2 = VideoFactory()
        video_3 = VideoFactory()
        # Second component of the graph.
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

    def test_must_return_non_connected_entities(self):
        self.client.force_authenticate(self.user_1)

        response = self.client.get(
            f"{self.user_base_url}/{self.video_source.uid}/",
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(
            list(map(lambda x: x["uid"], response.data["results"])),
            list(map(lambda x: x.uid, self.unrelated_video)),
        )
