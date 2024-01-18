from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models import User
from core.tests.factories.user import UserFactory
from core.utils.time import time_ago
from tournesol.tests.factories.comparison import ComparisonFactory
from tournesol.tests.factories.entity import EntityFactory, VideoFactory

from ..models import Comparison, Entity
from .factories.poll import PollWithCriteriasFactory


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
            date_joined=time_ago(days=90),
        )
        self._list_of_users = [user_1, user_2]

        video_1 = VideoFactory(
            metadata__uploader="uploader1",
            n_comparisons=2,
        )
        video_2 = VideoFactory(
            metadata__uploader="uploader2",
            n_comparisons=3,
        )
        video_3 = VideoFactory(
            metadata__uploader="uploader2",
            n_comparisons=4,
        )

        EntityFactory(type="another_type", n_comparisons=5)

        Entity.objects.filter(pk=video_1.pk).update(add_time=time_ago(days=5))
        Entity.objects.filter(pk=video_2.pk).update(add_time=time_ago(days=29))
        Entity.objects.filter(pk=video_3.pk).update(add_time=time_ago(days=60))

        self._list_of_videos = [video_1, video_2, video_3]

        comparison_1 = ComparisonFactory(
            user=user_1,
            entity_1=video_1,
            entity_2=video_2,
            duration_ms=102,
        )
        comparison_2 = ComparisonFactory(
            user=user_2,
            entity_1=video_1,
            entity_2=video_3,
            duration_ms=104,
        )
        comparison_3 = ComparisonFactory(
            user=user_2,
            entity_1=video_2,
            entity_2=video_3,
            duration_ms=302,
        )

        Comparison.objects.filter(pk=comparison_1.pk).update(
            datetime_add=time_ago(days=0)
        )
        Comparison.objects.filter(pk=comparison_2.pk).update(
            datetime_add=time_ago(days=7)
        )
        Comparison.objects.filter(pk=comparison_3.pk).update(
            datetime_add=time_ago(days=60)
        )

        self._list_of_comparisons = [comparison_1, comparison_2, comparison_3]

    def test_video_stats(self):
        """
        An anonymous user can get statistics about videos.
        """

        client = APIClient()

        response = client.get(
            reverse("tournesol:statistics_detail"),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        polls = response.data["polls"]
        video_poll = [poll for poll in polls if poll["name"] == "videos"][0]

        video_count = video_poll["compared_entities"]["total"]

        self.assertEqual(video_count, len(self._list_of_videos))
        self.assertEqual(video_poll["compared_entities"]["added_last_30_days"], 2)

        comparison_count = video_poll["comparisons"]["total"]
        last_30_days_comparison_count = video_poll["comparisons"]["added_last_30_days"]
        current_week_comparison_count = video_poll["comparisons"]["added_current_week"]

        self.assertEqual(comparison_count, len(self._list_of_comparisons))
        self.assertEqual(last_30_days_comparison_count, 2)
        self.assertEqual(current_week_comparison_count, 1)


    def test_user_stats(self):
        """
        An anonymous user can get statistics about users.
        """

        client = APIClient()

        response = client.get(
            reverse("tournesol:statistics_detail"),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        active_users = response.data["active_users"]
        user_count = active_users["total"]

        self.assertEqual(user_count, len(self._list_of_users))
        self.assertEqual(active_users["joined_last_30_days"], 1)

    def test_url_param_poll(self):
        """
        The `poll` URL parameter allows to filter the returned results by
        poll.
        """
        client = APIClient()

        new_poll = "new_poll"
        new_user = "new_user"

        response = client.get("/stats/")
        data = response.data

        self.assertEqual(len(data["polls"]), 2)
        for poll in data["polls"]:
            self.assertNotEqual(poll["name"], new_poll)

        poll = PollWithCriteriasFactory.create(name=new_poll)
        user = UserFactory(username=new_user)
        ComparisonFactory.create_batch(8, poll=poll, user=user)

        response = client.get("/stats/")
        data = response.data
        self.assertEqual(len(data["polls"]), 3)

        response = client.get("/stats/", {"poll": poll.name})
        data = response.data

        poll = [poll for poll in data["polls"] if poll["name"] == new_poll][0]
        self.assertEqual(len(data["polls"]), 1)
        self.assertEqual(poll["comparisons"]["total"], 8)

        # Using an unknown poll should return all polls.
        response = client.get("/stats/", {"poll": "unknown"})
        self.assertEqual(len(response.data["polls"]), 0)
