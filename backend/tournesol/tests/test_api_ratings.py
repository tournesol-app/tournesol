from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from core.models import User
from tournesol.models import Video, ContributorRating, ContributorRatingCriteriaScore


class RatingApi(TestCase):
    """
    TestCase of the Rating API.

    """
    _user = "user_with_one_video"
    _other_user = "random_user"

    def setUp(self):
        user1 = User.objects.create(username=self._user)
        user2 = User.objects.create(username=self._other_user)
        video1 = Video.objects.create(video_id='RD4g4XLGFTDG8')
        ContributorRating.objects.create(video=video1, user=user1)
        ContributorRating.objects.create(video=video1, user=user2)

    def test_anonymous_cant_list(self):
        factory = APIClient()
        response = factory.get(
            "/users/me/contributor_ratings/",
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_can_list(self):
        factory = APIClient()
        user = User.objects.get(username=self._user)
        factory.force_authenticate(user=user)
        response = factory.get(
            "/users/me/contributor_ratings/",
            args=[user.username],
            format="json"
        )
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_authenticated_cant_create(self):
        factory = APIClient()
        user = User.objects.get(username=self._user)
        factory.force_authenticate(user=user)
        response = factory.post(
            "/users/me/contributor_ratings/",
            {'video_id': 'NeADlWSDFAQ'},
            args=[user.username],
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_authenticated_fetch_non_existing_video(self):
        factory = APIClient()
        user = User.objects.get(username=self._user)
        factory.force_authenticate(user=user)
        response = factory.get(
            "/users/me/contributor_ratings/NeADlWSDFAQ/",
            args=[user.username],
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_authenticated_fetch_existing_video(self):
        factory = APIClient()
        user = User.objects.get(username=self._user)
        factory.force_authenticate(user=user)
        video = Video.objects.create(video_id='6QDWbKnwRcc')
        rating = ContributorRating.objects.create(video=video, user=user)
        ContributorRatingCriteriaScore.objects.create(
            contributor_rating=rating,
            criteria="test-criteria",
            score=1,
            uncertainty=2,
        )

        response = factory.get(
            "/users/me/contributor_ratings/6QDWbKnwRcc/",
            args=[user.username],
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["video"]["video_id"], '6QDWbKnwRcc')
        self.assertEqual(response.data["is_public"], False)
        self.assertEqual(response.data["criteria_scores"], [{
            "criteria": "test-criteria",
            "score": 1,
            "uncertainty": 2,
        }])
