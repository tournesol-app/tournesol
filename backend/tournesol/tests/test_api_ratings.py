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
        self.user1 = User.objects.create(username=self._user)
        self.user2 = User.objects.create(username=self._other_user)
        video1 = Video.objects.create(video_id='RD4g4XLGFTDG8')
        video2 = Video.objects.create(video_id='RD4g4XLGFTDG9')
        ContributorRating.objects.create(video=video1, user=self.user1, is_public=False)
        ContributorRating.objects.create(video=video1, user=self.user2, is_public=False)
        ContributorRating.objects.create(video=video2, user=self.user2, is_public=True)

    def test_anonymous_cant_list(self):
        factory = APIClient()
        response = factory.get(
            "/users/me/contributor_ratings/",
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_can_list(self):
        factory = APIClient()
        factory.force_authenticate(user=self.user1)
        response = factory.get(
            "/users/me/contributor_ratings/",
            format="json"
        )
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_authenticated_cant_create(self):
        factory = APIClient()
        factory.force_authenticate(user=self.user1)
        response = factory.post(
            "/users/me/contributor_ratings/",
            {'video_id': 'NeADlWSDFAQ'},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_authenticated_fetch_non_existing_video(self):
        factory = APIClient()
        factory.force_authenticate(user=self.user1)
        response = factory.get(
            "/users/me/contributor_ratings/NeADlWSDFAQ/",
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_authenticated_fetch_existing_video(self):
        factory = APIClient()
        user = self.user1
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

    def test_ratings_list_with_filter(self):
        client = APIClient()
        client.force_authenticate(self.user2)

        response = client.get(
            "/users/me/contributor_ratings/?is_public=false",
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["count"], 1)
        self.assertEqual(response.json()["results"][0]["video"]["video_id"], "RD4g4XLGFTDG8")

        response = client.get(
            "/users/me/contributor_ratings/?is_public=true",
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["count"], 1)
        self.assertEqual(response.json()["results"][0]["video"]["video_id"], "RD4g4XLGFTDG9")

    def test_patch_rating_is_public(self):
        client = APIClient()
        client.force_authenticate(self.user1)
        rating = ContributorRating.objects.get(user=self.user1)

        self.assertEqual(rating.is_public, False)
        response = client.patch(
            "/users/me/contributor_ratings/RD4g4XLGFTDG8/",
            data={"is_public": True},
            format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["is_public"], True, response.json())
        rating.refresh_from_db()
        self.assertEqual(rating.is_public, True)
