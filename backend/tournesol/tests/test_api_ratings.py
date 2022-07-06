from django.db.models import ObjectDoesNotExist
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from core.tests.factories.user import UserFactory
from tournesol.models import ContributorRating, Poll
from tournesol.tests.factories.comparison import ComparisonFactory
from tournesol.tests.factories.entity import VideoFactory
from tournesol.tests.factories.poll import PollFactory
from tournesol.tests.factories.ratings import (
    ContributorRatingCriteriaScoreFactory,
    ContributorRatingFactory,
)


class RatingApi(TestCase):
    """
    TestCase of the rating API.
    """

    def setUp(self):
        self.poll_videos = Poll.default_poll()
        self.ratings_base_url = "/users/me/contributor_ratings/{}/".format(
            self.poll_videos.name
        )

        self.client = APIClient()

        self.user1 = UserFactory()
        self.user2 = UserFactory()

        self.video1 = VideoFactory()
        self.video2 = VideoFactory()
        self.video3 = VideoFactory()

        ComparisonFactory(
            user=self.user1,
            entity_1=self.video1,
            entity_2=self.video2,
        )
        ContributorRatingFactory(user=self.user2, entity=self.video2, is_public=True)
        ComparisonFactory(
            user=self.user2,
            entity_1=self.video1,
            entity_2=self.video2,
        )

    def test_anonymous_cant_create(self):
        """
        An anonymous user can't create a rating for an existing video.
        """
        response = self.client.post(
            self.ratings_base_url, {"video_id": self.video3.video_id}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_cant_create_non_existing_poll(self):
        """
        An authenticated user can't create a rating in a non-existing poll.
        """
        self.client.force_authenticate(user=self.user1)
        non_existing_poll = "non-existing"

        response = self.client.post(
            "/users/me/contributor_ratings/{}/".format(non_existing_poll),
            {"video_id": self.video3.video_id},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # the non-existing poll must not be created
        with self.assertRaises(ObjectDoesNotExist):
            ContributorRating.objects.select_related("poll", "user", "entity").get(
                poll__name=non_existing_poll,
                user=self.user1,
                entity__uid=self.video3.uid,
            )

        # the default poll must not contain the rating
        with self.assertRaises(ObjectDoesNotExist):
            ContributorRating.objects.select_related("poll", "user", "entity").get(
                poll=self.poll_videos,
                user=self.user1,
                entity__uid=self.video3.uid,
            )

    def test_authenticated_can_create_with_existing_video(self):
        """
        An authenticated user can create a rating for an existing video. The
        rating is private by default.
        """
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(
            self.ratings_base_url, {"uid": self.video3.uid}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        rating = ContributorRating.objects.select_related("poll", "user", "entity").get(
            poll=self.poll_videos,
            user=self.user1,
            entity__uid=self.video3.uid,
        )
        self.assertEqual(rating.is_public, False)

    def test_authenticated_can_create_with_non_existing_video(self):
        """
        An authenticated user can create a rating even if the video is not
        already present in the database. The rating is private by default.
        """
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(
            self.ratings_base_url, {"uid": "yt:NeADlWSDFAQ"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        rating = ContributorRating.objects.select_related("poll", "user", "entity").get(
            poll=self.poll_videos, user=self.user1, entity__uid="yt:NeADlWSDFAQ"
        )
        self.assertEqual(rating.is_public, False)

    def test_authenticated_cannot_create_with_unknonwn_non_video_entity(self):
        poll2 = PollFactory(entity_type="candidate_fr_2022")

        self.client.force_authenticate(user=self.user1)
        response = self.client.post(
            f"/users/me/contributor_ratings/{poll2.name}/",
            data={"uid": "wd:Q42"},
            format="json"
        )
        self.assertContains(response, "entity has not been found", status_code=status.HTTP_400_BAD_REQUEST)

    def test_authenticated_can_create_rating_as_public(self):
        """
        An authenticated user can create a public rating.
        """
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(
            self.ratings_base_url,
            {"uid": self.video3.uid, "is_public": True},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.json())
        self.assertEqual(response.data["entity"]["uid"], self.video3.uid)
        self.assertEqual(response.data["is_public"], True)
        self.assertEqual(response.data["n_comparisons"], 0)

    def test_authenticated_cant_create_twice(self):
        """
        An authenticated user can't create two ratings for a single uid in a
        given poll.
        """
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(
            self.ratings_base_url,
            {"uid": self.video3.uid, "is_public": True},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.json())

        response = self.client.post(
            self.ratings_base_url,
            {"uid": self.video3.uid, "is_public": True},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_authenticated_cant_create_with_invalid_uid(self):
        """
        An authenticated user can't create a rating with an invalid uid.
        """
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(
            self.ratings_base_url, {"uid": "invalid"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_authenticated_cant_fetch_non_existing_entity(self):
        """
        An authenticated user can't fetch its rating about a non-existing
        entity.
        """
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(
            "{}{}/".format(self.ratings_base_url, "yt:NeADlWSDFAQ"), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_authenticated_can_fetch_existing_entity(self):
        """
        An authenticated user can fetch its rating about an existing entity,
        in a given poll.
        """
        self.client.force_authenticate(user=self.user1)
        video = VideoFactory()
        rating = ContributorRatingFactory(user=self.user1, entity=video)
        ContributorRatingCriteriaScoreFactory(
            contributor_rating=rating,
            criteria="test-criteria",
            score=1,
            uncertainty=2,
        )

        response = self.client.get(
            "{}{}/".format(self.ratings_base_url, video.uid), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["entity"]["uid"], video.uid)
        self.assertEqual(response.data["is_public"], False)
        self.assertEqual(
            response.data["criteria_scores"],
            [
                {
                    "criteria": "test-criteria",
                    "score": 1,
                    "uncertainty": 2,
                }
            ],
        )
        self.assertEqual(response.data["n_comparisons"], 0)

    def test_anonymous_cant_list(self):
        """
        An anonymous user can't list its ratings.
        """
        response = self.client.get(
            self.ratings_base_url,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_can_list(self):
        """
        An authenticated user can list its ratings related to a poll.
        """
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.ratings_base_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        rating = response.data["results"][0]
        self.assertEqual(rating["entity"]["uid"], self.video2.uid)
        self.assertEqual(rating["is_public"], False)
        self.assertEqual(rating["n_comparisons"], 1)

    def test_authenticated_can_list_with_filter(self):
        """
        An authenticated user can list its ratings filtered by the
        public/private status, in a given poll.
        """
        self.client.force_authenticate(self.user2)

        # get private ratings
        response = self.client.get(
            "{}?is_public=false".format(self.ratings_base_url), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json_resp = response.json()

        self.assertEqual(json_resp["count"], 1)
        self.assertEqual(json_resp["results"][0]["entity"]["uid"], self.video1.uid)

        # get public ratings
        response = self.client.get(
            "{}?is_public=true".format(self.ratings_base_url), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json_resp = response.json()

        self.assertEqual(json_resp["count"], 1)
        self.assertEqual(json_resp["results"][0]["entity"]["uid"], self.video2.uid)

    def test_anonymous_cant_update_public_status(self):
        """
        An anonymous user can't update the public/private status of a rating,
        in a given poll.
        """
        rating = ContributorRating.objects.get(
            poll=self.poll_videos, user=self.user1, entity=self.video1
        )
        self.assertEqual(rating.is_public, False)

        response = self.client.patch(
            "{}{}/".format(self.ratings_base_url, self.video1.uid),
            data={"is_public": True},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        rating.refresh_from_db()
        self.assertEqual(rating.is_public, False)

    def test_authenticated_can_update_public_status(self):
        """
        An authenticated user can update the public/private status of its
        rating, in a given poll.
        """
        self.client.force_authenticate(self.user1)
        rating = ContributorRating.objects.get(
            poll=self.poll_videos, user=self.user1, entity=self.video1
        )
        self.assertEqual(rating.is_public, False)

        # Create contributor score, that will be returned in the PATCH response
        ContributorRatingCriteriaScoreFactory(
            contributor_rating=rating,
            criteria="test-criteria",
            score=3,
        )

        response = self.client.patch(
            "{}{}/".format(self.ratings_base_url, self.video1.uid),
            data={"is_public": True},
            format="json",
        )
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_data["is_public"], True)
        self.assertEqual(
            response_data["criteria_scores"],
            [
                {
                    "criteria": "test-criteria",
                    "score": 3.0,
                    "uncertainty": 0.0,
                }
            ],
        )
        rating.refresh_from_db()
        self.assertEqual(rating.is_public, True)

    def test_authenticated_can_update_public_status_all(self):
        """
        An authenticated user can update the public/private status of all its
        ratings, in a given poll.
        """
        self.client.force_authenticate(self.user1)

        user1_private_ratings = self.user1.contributorvideoratings.filter(
            is_public=True
        ).count()
        user2_private_ratings = self.user2.contributorvideoratings.filter(
            is_public=True
        ).count()

        self.assertEqual(self.user1.contributorvideoratings.count(), 2)
        self.assertEqual(user1_private_ratings, 0)
        self.assertEqual(user2_private_ratings, 1)

        response = self.client.patch(
            "{}_all/".format(self.ratings_base_url), data={"is_public": False}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            self.user1.contributorvideoratings.filter(is_public=False).count(), 2
        )
        self.assertEqual(
            self.user2.contributorvideoratings.filter(is_public=False).count(),
            user2_private_ratings,
        )

    def test_anonymous_cant_update_public_status_all(self):
        """
        An anonymous user can't update the public/private status of a list of
        ratings, in a given poll.
        """
        user2_private_ratings = self.user2.contributorvideoratings.filter(
            is_public=False
        ).count()

        self.assertEqual(self.user2.contributorvideoratings.count(), 2)
        self.assertEqual(user2_private_ratings, 1)

        response = self.client.patch(
            "{}_all/".format(self.ratings_base_url), data={"is_public": False}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # the number of private ratings of the user2 must not have changed
        self.assertEqual(
            self.user2.contributorvideoratings.filter(is_public=False).count(),
            user2_private_ratings,
        )
