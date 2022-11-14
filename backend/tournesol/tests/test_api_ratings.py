from datetime import timedelta

from django.db.models import ObjectDoesNotExist
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from core.tests.factories.user import UserFactory
from tournesol.models import Comparison, ContributorRating, Poll
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
        self.comparison_user2 = ComparisonFactory(
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
            format="json",
        )
        self.assertContains(
            response,
            "entity has not been found",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

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

    def test_authenticated_can_list_ordered_by_n_comparisons(self):
        """
        An authenticated user can list its ratings related to a poll by the
        number of comparisons.
        """
        new_user = UserFactory()

        self.client.force_authenticate(user=new_user)

        new_video1 = VideoFactory()
        new_video2 = VideoFactory()
        new_video3 = VideoFactory()
        new_video4 = VideoFactory()

        ContributorRatingFactory(user=new_user, entity=new_video1, is_public=True)
        ContributorRatingFactory(user=new_user, entity=new_video2, is_public=True)
        ContributorRatingFactory(user=new_user, entity=new_video3, is_public=True)
        ContributorRatingFactory(user=new_user, entity=new_video4, is_public=True)

        # new_video1 has 3 comparisons
        for entity_b in [new_video2, new_video3, new_video4]:
            ComparisonFactory(
                user=new_user,
                entity_1=new_video1,
                entity_2=entity_b,
            )

        # new_video2 has 2 comparisons
        for entity_b in [new_video3]:
            ComparisonFactory(
                user=new_user,
                entity_1=new_video2,
                entity_2=entity_b,
            )

        # The least compared first.
        response = self.client.get(self.ratings_base_url + "?order_by=n_comparisons")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [r["n_comparisons"] for r in response.data["results"]], [1, 2, 2, 3]
        )

        # The most compared first.
        response = self.client.get(self.ratings_base_url + "?order_by=-n_comparisons")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [r["n_comparisons"] for r in response.data["results"]], [3, 2, 2, 1]
        )

    def test_authenticated_can_list_ordered_by_last_compared_at(self):
        """
        An authenticated user can list its ratings related to a poll by the
        last comparison date.
        """

        video_old1 = VideoFactory()
        video_old2 = VideoFactory()
        video_recent1 = VideoFactory()
        video_recent2 = VideoFactory()

        ContributorRatingFactory(user=self.user2, entity=video_old1, is_public=True)
        ContributorRatingFactory(user=self.user2, entity=video_old2, is_public=True)
        ContributorRatingFactory(user=self.user2, entity=video_recent1, is_public=True)
        ContributorRatingFactory(user=self.user2, entity=video_recent2, is_public=True)

        comp_old = ComparisonFactory(
            user=self.user2,
            entity_1=video_old1,
            entity_2=video_old2,
        )

        comp_recent = ComparisonFactory(
            user=self.user2,
            entity_1=video_recent1,
            entity_2=video_recent2,
        )

        ten_days_ago = self.comparison_user2.datetime_lastedit - timedelta(days=10)
        ten_days_ahead = self.comparison_user2.datetime_lastedit + timedelta(days=10)
        # update() allows to bypass the auto_now=True of the `datetime_lastedit` field.
        Comparison.objects.filter(pk=comp_old.pk).update(datetime_lastedit=ten_days_ago)
        Comparison.objects.filter(pk=comp_recent.pk).update(
            datetime_lastedit=ten_days_ahead
        )

        self.client.force_authenticate(user=self.user2)

        # The oldest first
        response = self.client.get(
            self.ratings_base_url + "?order_by=last_compared_at",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        sorted_array = sorted(
            response.data["results"], key=lambda x: x["last_compared_at"]
        )
        self.assertEqual(
            response.data["results"], sorted_array, response.data["results"]
        )
        # The most recent first
        response = self.client.get(
            self.ratings_base_url + "?order_by=-last_compared_at",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        sorted_array = sorted(
            response.data["results"], key=lambda x: x["last_compared_at"], reverse=True
        )
        self.assertEqual(response.data["results"], sorted_array)

    def test_authenticated_can_list_videos_by_duration(self):
        """
        An authenticated user can list its ratings related to the `videos`
        poll by the entities' duration.
        """

        self.client.force_authenticate(user=self.user1)

        metadata1 = self.video1.metadata
        metadata2 = self.video2.metadata
        metadata1["duration"] = 10
        metadata2["duration"] = 20
        self.video1.metadata = metadata1
        self.video2.metadata = metadata2
        self.video1.save(update_fields=["metadata"])
        self.video2.save(update_fields=["metadata"])

        response = self.client.get(
            self.ratings_base_url + "?order_by=duration", format="json"
        )
        results = response.data["results"]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(results[0]["entity"]["uid"], self.video1.uid)
        self.assertEqual(results[1]["entity"]["uid"], self.video2.uid)

        response = self.client.get(
            self.ratings_base_url + "?order_by=-duration", format="json"
        )
        results = response.data["results"]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(results[0]["entity"]["uid"], self.video2.uid)
        self.assertEqual(results[1]["entity"]["uid"], self.video1.uid)

    def test_authenticated_can_list_videos_by_publication_date(self):
        """
        An authenticated user can list its ratings related to the `videos`
        poll by the entities' publication date.
        """

        self.client.force_authenticate(user=self.user1)

        metadata1 = self.video1.metadata
        metadata2 = self.video2.metadata

        ten_day_sago = timezone.datetime.fromisoformat(
            metadata2["publication_date"]
        ) - timedelta(days=10)
        metadata1["publication_date"] = str(ten_day_sago)

        self.video1.metadata = metadata1
        self.video1.save(update_fields=["metadata"])

        response = self.client.get(
            self.ratings_base_url + "?order_by=publication_date", format="json"
        )
        results = response.data["results"]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(results[0]["entity"]["uid"], self.video1.uid)
        self.assertEqual(results[1]["entity"]["uid"], self.video2.uid)

        response = self.client.get(
            self.ratings_base_url + "?order_by=-publication_date", format="json"
        )
        results = response.data["results"]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(results[0]["entity"]["uid"], self.video2.uid)
        self.assertEqual(results[1]["entity"]["uid"], self.video1.uid)

    def test_authenticated_cannot_list_with_invalid_order_by(self):
        """
        An authenticated user cannot list its ratings related to a poll with
        an invalid `order_by` parameter
        """
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(
            self.ratings_base_url + "?order_by=INVALID", format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

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
