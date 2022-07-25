from unittest.mock import ANY

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from core.models import User
from core.tests.factories.user import UserFactory
from tournesol.models import Entity, Poll, RateLater
from tournesol.tests.factories.comparison import ComparisonFactory
from tournesol.tests.factories.entity import RateLaterFactory, VideoFactory
from tournesol.tests.factories.poll import PollFactory


class RateLaterListTestCase(TestCase):
    """
    TestCase of the `RateLaterList` API.
    """

    _user = "username"
    _invalid_poll_name = "invalid"

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = UserFactory(username=self._user)

        self.poll = PollFactory()
        self.rate_later_base_url = f"/users/me/rate_later/{self.poll.name}/"

        self.entity_in_ratelater = VideoFactory()
        self.entity_not_in_ratelater = VideoFactory()

        self.to_rate_later = RateLater.objects.create(
            entity=self.entity_in_ratelater,
            user=self.user,
            poll=self.poll,
        )
        self.maxDiff = None

    def test_anon_401_list(self) -> None:
        """
        An anonymous user cannot list its rate-later items, even if the poll
        exists.
        """
        response = self.client.get(self.rate_later_base_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anon_401_list_invalid_poll(self) -> None:
        """
        An anonymous user cannot list its rate-later items, even if the poll
        doesn't exist.
        """
        response = self.client.get(f"/users/me/rate_later/{self._invalid_poll_name}/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_auth_200_list(self) -> None:
        """
        An authenticated user can list its rate-later items from a specific
        poll.
        """
        self.client.force_authenticate(self.user)
        response = self.client.get(self.rate_later_base_url)

        results = response.data["results"]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

        self.assertDictEqual(
            results[0],
            {
                "entity": {
                    "uid": self.to_rate_later.entity.uid,
                    "type": "video",
                    "metadata": ANY,
                },
                "created_at": str(
                    self.to_rate_later.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                ),
            },
            results[0],
        )

    def test_auth_200_list_is_poll_specific(self) -> None:
        """
        Rate-later items are saved per poll.
        """
        other_poll = PollFactory()
        RateLater.objects.create(
            entity=self.entity_not_in_ratelater,
            user=self.user,
            poll=other_poll,
        )

        # The rate-later list of the poll `self.poll` must contain only the
        # entity `self.entity_in_ratelater`.
        self.client.force_authenticate(self.user)
        response = self.client.get(self.rate_later_base_url)
        results = response.data["results"]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(results[0]["entity"]["uid"], self.entity_in_ratelater.uid)

        # The rate-later list of the poll `other_poll` must contain only the
        # entity `self.entity_not_in_ratelater`.
        response = self.client.get(f"/users/me/rate_later/{other_poll.name}/")
        results = response.data["results"]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(results[0]["entity"]["uid"], self.entity_not_in_ratelater.uid)

    def test_auth_404_list_invalid_poll(self) -> None:
        """
        An authenticated user cannot list its rate-later items from a
        non-existing poll.
        """
        self.client.force_authenticate(self.user)
        response = self.client.get(f"/users/me/rate_later/{self._invalid_poll_name}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_anon_401_post(self) -> None:
        """
        An anonymous user cannot add an entity to its rate-later list, even if
        the poll exists.
        """
        data = {"entity": {"uid": "yt:xSqqXN0D4fY"}}
        response = self.client.post(self.rate_later_base_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anon_401_post_invalid_poll(self) -> None:
        """
        An anonymous user cannot add an entity to its rate-later list, even if
        the poll doesn't exist.
        """
        data = {"entity": {"uid": "yt:xSqqXN0D4fY"}}
        response = self.client.post(
            f"/users/me/rate_later/{self._invalid_poll_name}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_auth_201_post(self) -> None:
        """
        An authenticated user can add an entity to its rate-later list from a
        specific poll.
        """
        other_poll = PollFactory()
        self.client.force_authenticate(self.user)

        initial_nbr = RateLater.objects.filter(poll=self.poll, user=self.user).count()

        data = {"entity": {"uid": "yt:xSqqXN0D4fY"}}
        response = self.client.post(self.rate_later_base_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqualt(
            RateLater.objects.filter(poll=self.poll, user=self.user).count(),
            initial_nbr + 1,
        )

        # Rate-later items are saved per poll.
        self.assertEqualt(
            RateLater.objects.filter(poll=other_poll, user=self.user).count(), 0
        )

    def test_auth_404_post_invalid_poll(self) -> None:
        """
        An authenticated user cannot add an entity in a rate-later list from a
        non-existing poll.
        """
        self.client.force_authenticate(self.user)
        data = {"entity": {"uid": "yt:xSqqXN0D4fY"}}
        response = self.client.post(
            f"/users/me/rate_later/{self._invalid_poll_name}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class RateLaterDetailTestCase(TestCase):
    """
    TestCase of the `RateLaterDetail` API.
    """

    pass


class LegacyRateLaterApi(TestCase):
    """
    TestCase of the legacy RateLater API.

    For each endpoint, the TestCase performs the following tests:
        - authorization checks
        - permission checks
        - behaviour checks
    """

    # the username of a user with on video to rate later
    _user = "user_with_one_video"
    # the username of another user with one video to rate later
    _other = "other_user_with_one_video"

    # video name in _user's rate later list
    _users_video = "video_in_users_ratelater_list"
    # video name in _other's  rate later list
    _others_video = "video_in_others_ratelater_list"

    def setUp(self):
        """
        Set-up a minimal set of data to test the RateLater API.

        At least two users are required, each of them having a distinct rate
        later list.
        """
        self.default_poll = Poll.default_poll()

        user1 = UserFactory(username=self._user)
        user2 = UserFactory(username=self._other)

        video1 = VideoFactory(metadata__name=self._users_video)
        video2 = VideoFactory(metadata__name=self._others_video)

        RateLaterFactory(user=user1, entity=video1)
        RateLaterFactory(user=user2, entity=video2)

    def test_anonymous_cant_list(self):
        """
        An anonymous user can't display someone else's rate later list.
        """
        client = APIClient()
        response = client.get("/users/me/video_rate_later/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_can_list(self):
        """
        An authenticated user can display its own rate later list.
        """
        client = APIClient()

        user = User.objects.get(username=self._user)
        video_rate_later = RateLater.objects.select_related("entity").filter(user=user)
        client.force_authenticate(user=user)

        # authorization check
        response = client.get("/users/me/video_rate_later/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # user must see only its own rate later list
        self.assertEqual(len(response.data["results"]), video_rate_later.count())
        self.assertEqual(
            response.data["results"][0]["video"]["video_id"],
            video_rate_later[0].entity.video_id,
        )

    def test_authenticated_cant_list_others(self):
        """
        An authenticated user can't display someone else's rate later list.
        """
        client = APIClient()

        user = User.objects.get(username=self._user)
        other = User.objects.get(username=self._other)

        client.force_authenticate(user=user)

        response = client.get(f"/users/{other.username}/video_rate_later/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_anonymous_cant_create(self):
        """
        An anonymous user can't add a video.
        """
        client = APIClient()
        data = {"video.video_id": "random_video_id"}

        response = client.post(
            "/users/me/video_rate_later/",
            data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_can_create(self):
        """
        An authenticated user can add in its own rate later list a video
        existing in the database.
        """
        client = APIClient()

        user = User.objects.get(username=self._user)
        data = {
            "video": {
                "video_id": Entity.objects.get(
                    metadata__name=self._others_video
                ).video_id
            }
        }

        client.force_authenticate(user=user)

        response = client.post(
            "/users/me/video_rate_later/",
            data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.json())

    def test_authenticated_can_create_with_new_video_id(self):
        """
        An authenticated user can add in its own rate later list a video
        that does not exist yet in the database.
        """
        client = APIClient()

        user = User.objects.get(username=self._user)
        data = {"video": {"video_id": "newvideo001"}}

        client.force_authenticate(user=user)
        response = client.post(
            "/users/me/video_rate_later/",
            data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

    def test_authenticated_cant_create_twice(self):
        """
        An authenticated user can't add in its own rate later list a video
        already in its rate later list.
        """
        client = APIClient()

        user = User.objects.get(username=self._user)
        data = {
            "video": {
                "video_id": Entity.objects.get(
                    metadata__name=self._users_video
                ).video_id
            }
        }

        client.force_authenticate(user=user)

        response = client.post(
            "/users/me/video_rate_later/",
            data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_authenticated_cant_create_others(self):
        """
        An authenticated user can't add a video in someone else's rate later
        list.
        """
        client = APIClient()

        user = User.objects.get(username=self._user)
        other = User.objects.get(username=self._other)
        data = {
            "video": {
                "video_id": Entity.objects.get(
                    metadata__name=self._users_video
                ).video_id
            }
        }

        client.force_authenticate(user=user)

        response = client.post(
            f"/users/{other.username}/video_rate_later/",
            data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_anonymous_cant_fetch(self):
        """
        An anonymous user can't fetch a video from someone else's rate later
        list.
        """
        client = APIClient()
        user = User.objects.get(username=self._user)
        response = client.get("/users/me/video_rate_later/non-existing-video-id/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_can_fetch(self):
        """
        An authenticated user can fetch a video from its own rate later list.
        """
        client = APIClient()

        user = User.objects.get(username=self._user)
        video = Entity.objects.get(metadata__name=self._users_video)

        client.force_authenticate(user=user)

        response = client.get(
            f"/users/me/video_rate_later/{video.video_id}/",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_anonymous_cant_delete(self):
        """
        An anonymous user can't delete a video from someone else's rate later
        list.
        """
        client = APIClient()
        response = client.delete(f"/users/me/video_rate_later/a-video-id/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_can_delete(self):
        """
        An authenticated user can delete a video from its own rate later list.
        """
        client = APIClient()

        user = User.objects.get(username=self._user)
        video = Entity.objects.get(metadata__name=self._users_video)

        client.force_authenticate(user=user)

        self.assertEqual(user.ratelaters.count(), 1)
        response = client.delete(f"/users/me/video_rate_later/{video.video_id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(user.ratelaters.count(), 0)

    def test_automatically_removed_after_4_comparisons(self):
        """
        Test the automated removal from the rate later list.
        """
        user = User.objects.get(username=self._user)
        other_user = User.objects.get(username=self._other)
        video = RateLater.objects.filter(user=user).first().entity

        # Video should not be removed after 2 comparisons
        ComparisonFactory(user=user, entity_2=video)
        ComparisonFactory(user=user, entity_1=video)
        video.auto_remove_from_rate_later(self.default_poll, user)
        self.assertEqual(RateLater.objects.filter(user=user, entity=video).count(), 1)

        # Video is not removed when compared by other user
        ComparisonFactory(user=other_user, entity_2=video)
        ComparisonFactory(user=other_user, entity_2=video)
        ComparisonFactory(user=other_user, entity_1=video)
        ComparisonFactory(user=other_user, entity_1=video)
        video.auto_remove_from_rate_later(self.default_poll, user)
        self.assertEqual(RateLater.objects.filter(user=user, entity=video).count(), 1)

        # Video should not be removed after 3 comparisons
        ComparisonFactory(user=user, entity_2=video)
        video.auto_remove_from_rate_later(self.default_poll, user)
        self.assertEqual(RateLater.objects.filter(user=user, entity=video).count(), 1)

        # Video is not removed when comparing unrelated videos
        ComparisonFactory(user=user)
        ComparisonFactory(user=user)
        video.auto_remove_from_rate_later(self.default_poll, user)
        self.assertEqual(RateLater.objects.filter(user=user, entity=video).count(), 1)

        # Video should be removed after 4 comparisons
        ComparisonFactory(user=user, entity_2=video)
        video.auto_remove_from_rate_later(self.default_poll, user)
        self.assertEqual(RateLater.objects.filter(user=user, entity=video).count(), 0)

        # Video can be added again
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post(
            "/users/me/video_rate_later/",
            {"video": {"video_id": video.video_id}},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.json())
        self.assertEqual(RateLater.objects.filter(user=user, entity=video).count(), 1)

        # Video is removed again after one new comparison
        ComparisonFactory(user=user, entity_2=video)
        video.auto_remove_from_rate_later(self.default_poll, user)
        self.assertEqual(RateLater.objects.filter(user=user, entity=video).count(), 0)
