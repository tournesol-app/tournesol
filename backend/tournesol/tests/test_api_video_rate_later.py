from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models import User
from tournesol.models import Video, VideoRateLater


class VideoRateLaterApi(TestCase):
    """
    TestCase of the VideoRateLater API.

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
        Set-up a minimal set of data to test the VideoRateLater API.

        At least two users are required, each of them having a distinct rate
        later list.
        """
        user1 = User.objects.create(username=self._user)
        user2 = User.objects.create(username=self._other)

        video1 = Video.objects.create(
            video_id="test_video_id_1", name=self._users_video
        )

        video2 = Video.objects.create(
            video_id="test_video_id_2", name=self._others_video
        )

        VideoRateLater.objects.create(user=user1, video=video1)
        VideoRateLater.objects.create(user=user2, video=video2)

    def test_anonymous_cant_list(self):
        """
        An anonymous user can't display someone else's rate later list.
        """
        client = APIClient()
        user = User.objects.get(username=self._user)
        response = client.get(
            reverse("tournesol:video_rate_later_list", args=[user.username])
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_can_list(self):
        """
        An authenticated user can display its own rate later list.
        """
        client = APIClient()

        user = User.objects.get(username=self._user)
        video_rate_later = VideoRateLater.objects.select_related("video").filter(
            user=user
        )
        client.force_authenticate(user=user)

        # authorization check
        response = client.get(
            reverse("tournesol:video_rate_later_list", args=[user.username])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # user must see only its own rate later list
        self.assertEqual(len(response.data["results"]), video_rate_later.count())
        self.assertEqual(
            response.data["results"][0]["video"]["video_id"],
            video_rate_later[0].video.video_id,
        )

    def test_authenticated_cant_list_others(self):
        """
        An authenticated user can't display someone else's rate later list.
        """
        client = APIClient()

        user = User.objects.get(username=self._user)
        other = User.objects.get(username=self._other)

        client.force_authenticate(user=user)

        response = client.get(
            reverse("tournesol:video_rate_later_list", args=[other.username])
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymous_cant_create(self):
        """
        An anonymous user can't add a video.
        """
        client = APIClient()

        user = User.objects.get(username=self._user)
        data = {"video.video_id": "random_video_id"}

        response = client.post(
            reverse("tournesol:video_rate_later_list", args=[user.username]),
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
        data = {"video": {"video_id": Video.objects.get(name=self._others_video).video_id}}

        client.force_authenticate(user=user)

        response = client.post(
            reverse("tournesol:video_rate_later_list", args=[user.username]),
            data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_authenticated_cant_create_twice(self):
        """
        An authenticated user can't add in its own rate later list a video
        already in its rate later list.
        """
        client = APIClient()

        user = User.objects.get(username=self._user)
        data = {"video": {"video_id": Video.objects.get(name=self._users_video).video_id}}

        client.force_authenticate(user=user)

        response = client.post(
            reverse("tournesol:video_rate_later_list", args=[user.username]),
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
        data = {"video": {"video_id": Video.objects.get(name=self._users_video).video_id}}

        client.force_authenticate(user=user)

        response = client.post(
            reverse("tournesol:video_rate_later_list", args=[other.username]),
            data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymous_cant_fetch(self):
        """
        An anonymous user can't fetch a video from someone else's rate later
        list.
        """
        client = APIClient()
        user = User.objects.get(username=self._user)
        response = client.get(
            reverse(
                "tournesol:video_rate_later_detail",
                args=[user.username, "non_existing_video_id"],
            )
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_can_fetch(self):
        """
        An authenticated user can fetch a video from its own rate later list.
        """
        client = APIClient()

        user = User.objects.get(username=self._user)
        video = Video.objects.get(name=self._users_video)

        client.force_authenticate(user=user)

        response = client.get(
            reverse("tournesol:video_rate_later_detail", args=[user.username, video.video_id])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_authenticated_cant_fetch_others(self):
        """
        An authenticated user can't fetch a video from someone else's rate
        later list.
        """
        client = APIClient()

        user = User.objects.get(username=self._user)
        other = User.objects.get(username=self._other)
        video = Video.objects.get(name=self._others_video)

        client.force_authenticate(user=user)

        response = client.get(
            reverse(
                "tournesol:video_rate_later_detail", args=[other.username, video.video_id]
            )
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymous_cant_delete(self):
        """
        An anonymous user can't delete a video from someone else's rate later
        list.
        """
        client = APIClient()
        user = User.objects.get(username=self._user)
        response = client.delete(
            reverse(
                "tournesol:video_rate_later_detail",
                args=[user.username, "non_existing_video_id"],
            )
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_can_delete(self):
        """
        An authenticated user can delete a video from its own rate later list.
        """
        client = APIClient()

        user = User.objects.get(username=self._user)
        video = Video.objects.get(name=self._users_video)

        client.force_authenticate(user=user)

        response = client.delete(
            reverse("tournesol:video_rate_later_detail", args=[user.username, video.video_id])
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_authenticated_cant_delete_others(self):
        """
        An authenticated user can't delete a video from someone else's rate
        later list.
        """
        client = APIClient()

        user = User.objects.get(username=self._user)
        other = User.objects.get(username=self._other)
        video = Video.objects.get(name=self._others_video)

        client.force_authenticate(user=user)

        response = client.delete(
            reverse(
                "tournesol:video_rate_later_detail", args=[other.username, video.video_id]
            )
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
