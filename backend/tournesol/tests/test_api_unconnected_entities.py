"""
All test cases related to the unconnected entities API.

For a given user, we consider entities and its comparisons as a graph. Entities
are vertices and comparisons edges.

See: https://en.wikipedia.org/wiki/Graph_(discrete_mathematics)
"""
import logging
import time

import numpy as np
import pytest
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from core.tests.factories.user import UserFactory
from tournesol.models import Comparison, Entity
from tournesol.models.entity import TYPE_VIDEO
from tournesol.models.poll import Poll
from tournesol.tests.factories.comparison import ComparisonFactory
from tournesol.tests.factories.entity import VideoFactory

logger = logging.getLogger(__name__)


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

    def test_non_strict_with_fully_unconnected_entity_returns_all(self):
        """
        The non-strict option used in the case of a video that is not connected
        to any other video should have no effect, because the goal of the
        strict option is to enable including distant-but-connected entities in
        the unconnected entities API route.
        """
        self.client.force_authenticate(self.user_1)

        response = self.client.get(
            f"{self.user_base_url}/{self.video_source.uid}/?strict=false",
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

        self.video_5 = VideoFactory()
        self.video_4 = VideoFactory()
        self.video_3 = VideoFactory()
        self.video_2 = VideoFactory()
        self.video_1 = VideoFactory()

        self.video_source = self.video_1

        ComparisonFactory(
            user=self.user_1,
            entity_1=self.video_3,
            entity_2=self.video_4,
        )
        ComparisonFactory(
            user=self.user_1,
            entity_1=self.video_2,
            entity_2=self.video_3,
        )
        ComparisonFactory(
            user=self.user_1,
            entity_1=self.video_1,
            entity_2=self.video_3,
        )
        ComparisonFactory(
            user=self.user_1,
            entity_1=self.video_1,
            entity_2=self.video_5,
        )
        ComparisonFactory(
            user=self.user_1,
            entity_1=self.video_2,
            entity_2=self.video_5,
        )

    def test_all_linked_must_return_empty(self):
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

    def test_non_strict_must_return_sorted_by_max_distance(self):
        """
        When using the option strict=false, an authenticated user must get a
        full list sorted by decreasing distance in the graph or comnparison to
        the target source entity.
        """
        self.client.force_authenticate(self.user_1)

        response = self.client.get(
            f"{self.user_base_url}/{self.video_source.uid}/?strict=false",
            format="json",
        )

        results = response.data["results"]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        # video 2 and 4 are both at distance 2 and should appear first, video 3 and 5 should
        # not appear because it has already been compared with the source entity. video 4 should
        # be first because it has a single comparison by the user against video 2 which has two.
        self.assertEqual(results[0]["entity"]["uid"], self.video_4.uid)
        self.assertEqual(results[1]["entity"]["uid"], self.video_2.uid)


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
        self.user_2 = UserFactory()
        self.poll_videos = Poll.default_poll()
        self.user_base_url = f"/users/me/unconnected_entities/{self.poll_videos.name}"

        self.video_1 = VideoFactory()
        self.video_2 = VideoFactory()
        self.video_3 = VideoFactory()
        self.video_4 = VideoFactory()
        self.video_5 = VideoFactory()
        # Distant entities.
        self.video_6 = VideoFactory()
        self.video_7 = VideoFactory()

        self.unrelated_video = [self.video_6, self.video_7]

        self.video_source = self.video_1

        # Comparisons from user 1
        for video_a, video_b in [
            (self.video_4, self.video_5),
            (self.video_2, self.video_4),
            (self.video_3, self.video_2),
            (self.video_3, self.video_1),  # 1 -> 3 -> 2 -> 4 -> 5
            (self.video_7, self.video_6),  # 6 & 7 are unconnected to the other entities
        ]:
            ComparisonFactory(
                user=self.user_1,
                entity_1=video_a,
                entity_2=video_b,
            )
        # Comparisons from user 2
        ComparisonFactory(
            user=self.user_2,
            entity_1=self.video_2,
            entity_2=self.video_6,
        )

    def test_must_return_non_connected_entities(self):
        self.client.force_authenticate(self.user_1)

        response = self.client.get(
            f"{self.user_base_url}/{self.video_source.uid}/",
            format="json",
        )
        results = response.data["results"]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(
            {res["entity"]["uid"] for res in results},
            {entity.uid for entity in self.unrelated_video},
        )

    def test_non_strict_must_return_non_connected_then_connected_sorted_by_distance(self):
        self.client.force_authenticate(self.user_1)

        response = self.client.get(
            f"{self.user_base_url}/{self.video_source.uid}/?strict=false",
            format="json",
        )
        results = response.data["results"]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # The response must contain firstly the two unconnected entities, and
        # the 4 other entities sorted by decreasing distance to the source
        # entity.
        self.assertEqual(response.data["count"], 5)
        uids = [res["entity"]["uid"] for res in results]
        self.assertEqual(set(uids[:2]), {entity.uid for entity in self.unrelated_video})
        self.assertEqual([self.video_5.uid,self.video_4.uid,self.video_2.uid], uids[2:])

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
        self.assertEqual(results[0]["entity"]["uid"], video_a.uid)

        # The 2nd and 3rd entities must be in the list of entities having 2
        # comparisons.
        self.assertIn(results[1]["entity"]["uid"], [video_b.uid, self.unrelated_video[1].uid])
        self.assertIn(results[2]["entity"]["uid"], [video_b.uid, self.unrelated_video[1].uid])

        # The fourth entity must be `self.unrelated_video[0]` with 3 comparisons.
        self.assertEqual(results[3]["entity"]["uid"], self.unrelated_video[0].uid)


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
        results = response.data["results"]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(
            {res["entity"]["uid"] for res in results},
            {entity.uid for entity in self.unrelated_video},
        )


@pytest.mark.django_db
@pytest.mark.parametrize("n_videos", [
    100,
    1000,
    2000,
    # Disabling the large test cases because they take a few minutes to run, but are useful for
    # checking the performance of the api call.
    # 5000,
    # 10000,
    # 20000,
    # 100000,
])
def test_non_strict_on_large_graph_should_be_fast(n_videos):
    client = APIClient()
    user_1 = UserFactory()
    poll_videos = Poll.default_poll()
    user_base_url = f"/users/me/unconnected_entities/{poll_videos.name}"

    # Creates n_videos videos
    begin = time.perf_counter()
    videos = Entity.objects.bulk_create([Entity(
        type=TYPE_VIDEO,
        uid=f"yt:video{k:06d}",
    ) for k in range(n_videos)], batch_size=2000)
    logger.debug("Created videos: %.3f seconds", time.perf_counter() - begin)

    # Creates comparisons for each videos 
    begin = time.perf_counter()
    Comparison.objects.bulk_create((
        Comparison(
            user=user_1,
            entity_1=video_a,
            entity_2=videos[k],
            poll=poll_videos,
        )
        for i, video_a in enumerate(videos)
        for k in np.random.choice(range(len(videos)), size=4, replace=False)
        if i < k
    ), batch_size=2000)
    logger.debug("Creating comparisons: %.3f seconds", time.perf_counter() - begin)

    client.force_authenticate(user_1)

    begin = time.perf_counter()
    response = client.get(
        f"{user_base_url}/{videos[0].uid}/?strict=false",
        format="json",
    )
    end = time.perf_counter()
    logger.debug("Api call: %.3f seconds", end - begin)
    assert end - begin < 1  # The API call takes less than 1 second
    assert response.status_code == status.HTTP_200_OK
