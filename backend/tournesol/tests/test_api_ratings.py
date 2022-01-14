from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from tournesol.models import ContributorRating
from tournesol.tests.factories.video import VideoFactory
from tournesol.tests.factories.comparison import ComparisonFactory
from core.tests.factories.user import UserFactory
from tournesol.tests.factories.ratings import ContributorRatingFactory, ContributorRatingCriteriaScoreFactory


class RatingApi(TestCase):
    """
    TestCase of the Rating API.

    """

    def setUp(self):
        self.user1 = UserFactory()
        self.user2 = UserFactory()
        self.video1 = VideoFactory()
        self.video2 = VideoFactory()
        self.video3 = VideoFactory()
        ComparisonFactory(video_1=self.video1, video_2=self.video2, user=self.user1)
        ComparisonFactory(video_1=self.video1, video_2=self.video2, user=self.user2)
        ContributorRatingFactory(video=self.video1, user=self.user1)
        ContributorRatingFactory(video=self.video2, user=self.user1)
        ContributorRatingFactory(video=self.video1, user=self.user2)
        ContributorRatingFactory(video=self.video2, user=self.user2, is_public=True)

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
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rating = response.data["results"][0]
        self.assertEqual(rating["video"]["video_id"], self.video2.video_id)
        self.assertEqual(rating["is_public"], False)
        self.assertEqual(rating["n_comparisons"], 1)

    def test_authenticated_cant_create_rating_about_non_existing_video(self):
        factory = APIClient()
        factory.force_authenticate(user=self.user1)
        response = factory.post(
            "/users/me/contributor_ratings/",
            {'video_id': 'NeADlWSDFAQ'},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_authenticated_initialize_rating_as_public(self):
        factory = APIClient()
        factory.force_authenticate(user=self.user1)
        response = factory.post(
            "/users/me/contributor_ratings/",
            {
                'video_id': self.video3.video_id,
                'is_public': True
            },
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["video"]["video_id"], self.video3.video_id)
        self.assertEqual(response.data["is_public"], True)
        self.assertEqual(response.data["n_comparisons"], 0)

        # Create the same rating object raises a validation error
        response = factory.post(
            "/users/me/contributor_ratings/",
            {
                'video_id': self.video3.video_id,
                'is_public': True
            },
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

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
        video = VideoFactory()
        rating = ContributorRatingFactory(video=video, user=user)
        ContributorRatingCriteriaScoreFactory(
            contributor_rating=rating,
            criteria="test-criteria",
            score=1,
            uncertainty=2,
        )

        response = factory.get(
            f"/users/me/contributor_ratings/{video.video_id}/",
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["video"]["video_id"], video.video_id)
        self.assertEqual(response.data["is_public"], False)
        self.assertEqual(response.data["criteria_scores"], [{
            "criteria": "test-criteria",
            "score": 1,
            "uncertainty": 2,
        }])
        self.assertEqual(response.data["n_comparisons"], 0)

    def test_ratings_list_with_filter(self):
        client = APIClient()
        client.force_authenticate(self.user2)

        response = client.get(
            "/users/me/contributor_ratings/?is_public=false",
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["count"], 1)
        self.assertEqual(response.json()["results"][0]["video"]["video_id"], self.video1.video_id)

        response = client.get(
            "/users/me/contributor_ratings/?is_public=true",
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["count"], 1)
        self.assertEqual(response.json()["results"][0]["video"]["video_id"], self.video2.video_id)

    def test_patch_rating_is_public(self):
        client = APIClient()
        client.force_authenticate(self.user1)
        rating = ContributorRating.objects.get(user=self.user1, video=self.video1)

        self.assertEqual(rating.is_public, False)
        response = client.patch(
            f"/users/me/contributor_ratings/{self.video1.video_id}/",
            data={"is_public": True},
            format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["is_public"], True, response.json())
        rating.refresh_from_db()
        self.assertEqual(rating.is_public, True)

    def test_patch_all_ratings(self):
        client = APIClient()
        client.force_authenticate(self.user2)
        self.assertEqual(self.user2.contributorvideoratings.count(), 2)
        self.assertEqual(self.user2.contributorvideoratings.filter(is_public=False).count(), 1)
        response = client.patch(
            "/users/me/contributor_ratings/_all/",
            data={"is_public": False}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.user2.contributorvideoratings.filter(is_public=False).count(), 2)
