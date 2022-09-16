from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from core.models import User
from tournesol.models import Poll
from tournesol.models.poll import ALGORITHM_MEHESTAN, DEFAULT_POLL_NAME
from tournesol.tests.factories.entity import (
    EntityFactory,
    UserFactory,
    VideoCriteriaScoreFactory,
    VideoFactory,
)
from tournesol.tests.factories.ratings import (
    ContributorRatingCriteriaScoreFactory,
    ContributorRatingFactory,
)


class PollsTestCase(TestCase):
    """
    TestCase of the PollsView API.
    """

    def test_anonymous_can_read(self):
        """An anonymous user can read a poll with its translated criteria."""
        client = APIClient(HTTP_ACCEPT_LANGUAGE="fr")
        response = client.get("/polls/videos/")
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data["name"], "videos")
        self.assertEqual(response_data["active"], True)
        self.assertEqual(response_data["entity_type"], "video")
        self.assertEqual(len(response_data["criterias"]), 10)
        self.assertEqual(
            response_data["criterias"][0],
            {
                "name": "largely_recommended",
                "label": "Devrait être largement recommandé",
                "optional": False,
            },
        )


class PollsRecommendationsTestCase(TestCase):
    """
    TestCase of the PollsRecommendationsView API.
    """

    def setUp(self):
        self.client = APIClient()

        self.video_1 = VideoFactory(
            metadata__publication_date="2021-01-01",
            metadata__uploader="_test_uploader_1",
            metadata__language="es",
            tournesol_score=-1,
            rating_n_contributors=2,
        )
        self.video_2 = VideoFactory(
            metadata__publication_date="2021-01-02",
            metadata__uploader="_test_uploader_2",
            metadata__language="fr",
            metadata__duration=10,
            tournesol_score=2.2,
            rating_n_contributors=3,
        )
        self.video_3 = VideoFactory(
            metadata__publication_date="2021-01-03",
            metadata__uploader="_test_uploader_2",
            metadata__language="pt",
            metadata__duration=120,
            tournesol_score=3.3,
            rating_n_contributors=4,
        )
        self.video_4 = VideoFactory(
            metadata__publication_date="2021-01-04",
            metadata__uploader="_test_uploader_3",
            metadata__language="it",
            metadata__duration=240,
            tournesol_score=4.4,
            rating_n_contributors=5,
        )

        VideoCriteriaScoreFactory(
            entity=self.video_1, criteria="reliability", score=-0.1
        )
        VideoCriteriaScoreFactory(
            entity=self.video_2, criteria="reliability", score=0.2
        )
        VideoCriteriaScoreFactory(entity=self.video_3, criteria="importance", score=0.3)
        VideoCriteriaScoreFactory(entity=self.video_4, criteria="importance", score=0.4)

        VideoCriteriaScoreFactory(
            entity=self.video_1,
            criteria="reliability",
            score=0.1,
            score_mode="all_equal",
        )
        VideoCriteriaScoreFactory(
            entity=self.video_2,
            criteria="reliability",
            score=-0.2,
            score_mode="all_equal",
        )
        VideoCriteriaScoreFactory(
            entity=self.video_3,
            criteria="importance",
            score=0.5,
            score_mode="all_equal",
        )
        VideoCriteriaScoreFactory(
            entity=self.video_4,
            criteria="importance",
            score=0.4,
            score_mode="all_equal",
        )

    def test_anonymous_can_list_recommendations(self):
        response = self.client.get("/polls/videos/recommendations/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data["results"]
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]["tournesol_score"], 4.4)
        self.assertEqual(results[1]["tournesol_score"], 3.3)
        self.assertEqual(results[2]["tournesol_score"], 2.2)

        self.assertEqual(results[0]["type"], "video")

    def test_ignore_score_attached_to_another_poll(self):
        other_poll = Poll.objects.create(name="other")
        video_5 = VideoFactory(
            metadata__publication_date="2021-01-05",
            rating_n_contributors=6,
        )
        VideoCriteriaScoreFactory(
            poll=other_poll, entity=video_5, criteria="importance", score=0.5
        )
        response = self.client.get("/polls/videos/recommendations/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 3)

    def test_anonymous_can_list_unsafe_recommendations(self):
        response = self.client.get("/polls/videos/recommendations/?unsafe=true")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 4)

    def test_anonymous_can_list_with_offset(self):
        """
        An anonymous user can list a subset of videos by using the `offset`
        query parameter.
        """
        response = self.client.get("/polls/videos/recommendations/?offset=2")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_list_videos_with_criteria_weights(self):
        # Default weights: all criterias contribute equally
        resp = self.client.get("/polls/videos/recommendations/")
        self.assertEqual(
            [r["uid"] for r in resp.data["results"]],
            [self.video_4.uid, self.video_3.uid, self.video_2.uid],
        )

        # Disable reliability
        resp = self.client.get("/polls/videos/recommendations/?weights[reliability]=0")
        self.assertEqual(
            # Only verifying the first two videos of the response because other videos
            # have only criteria scores for reliability
            [r["uid"] for r in resp.data["results"]][:2],
            [self.video_4.uid, self.video_3.uid],
        )

        # Disable both reliability and importance
        resp = self.client.get(
            "/polls/videos/recommendations/?weights[reliability]=0&weights[importance]=0"
        )
        self.assertEqual(len([r["uid"] for r in resp.data["results"]]), 3)

        # Disable both reliability and importance and specify unsafe
        resp = self.client.get(
            "/polls/videos/recommendations/?weights[reliability]=0&weights[importance]=0&unsafe=true"
        )
        self.assertEqual(len([r["uid"] for r in resp.data["results"]]), 4)

        # More weight to reliability should change the order
        resp = self.client.get(
            "/polls/videos/recommendations/?weights[reliability]=100&weights[importance]=10"
        )
        self.assertEqual(
            [r["uid"] for r in resp.data["results"]],
            [self.video_2.uid, self.video_4.uid, self.video_3.uid],
        )

    def test_anon_can_list_videos_filtered_by_metadata_single(self):
        """
        Anonymous users can filter the recommended videos using a single
        value filter.
        """
        resp = self.client.get(
            "/polls/videos/recommendations/?metadata[uploader]=_test_uploader_2"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [video["uid"] for video in resp.data["results"]],
            [self.video_3.uid, self.video_2.uid],
        )

        resp = self.client.get(
            "/polls/videos/recommendations/?metadata[uploader]=_test_uploader_3"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["results"][0]["uid"], self.video_4.uid)

        # filtering by an unknown single value metadata must return an empty list
        resp = self.client.get(
            "/polls/videos/recommendations/?metadata[uploader]=unknown_uploader"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["count"], 0)
        self.assertEqual(resp.data["results"], [])

    def test_anon_can_list_videos_filtered_by_metadata_multiple(self):
        """
        Anonymous users can filter the recommended videos using a multiple
        values filter.
        """
        resp = self.client.get("/polls/videos/recommendations/?metadata[language]=fr")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["results"][0]["uid"], self.video_2.uid)

        resp = self.client.get(
            "/polls/videos/recommendations/?metadata[language]=fr"
            "&metadata[language]=pt"
            "&metadata[language]=it"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [video["uid"] for video in resp.data["results"]],
            [self.video_4.uid, self.video_3.uid, self.video_2.uid],
        )

    def test_anon_can_list_videos_filtered_by_metadata_mixed(self):
        """
        Anonymous users can filter the recommended videos using a combination
        of single value and multiple values metadata filters.
        """
        resp = self.client.get(
            "/polls/videos/recommendations/?metadata[uploader]=_test_uploader_2"
            "&metadata[language]=fr&metadata[language]=pt&metadata[language]=it"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [video["uid"] for video in resp.data["results"]],
            [self.video_3.uid, self.video_2.uid],
        )

        resp = self.client.get(
            "/polls/videos/recommendations/?metadata[uploader]=unknown_uploader"
            "&metadata[language]=fr&metadata[language]=pt&metadata[language]=it"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["count"], 0)
        self.assertEqual(resp.data["results"], [])

    def test_anon_cannot_use_forbidden_strings_in_metadata_filter(self):
        response = self.client.get("/polls/videos/recommendations/?metadata[__]=10")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.get(
            "/polls/videos/recommendations/?metadata[duration__lte]=10"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.get(
            "/polls/videos/recommendations/?metadata[duration__lte::int]=10"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_anon_can_list_videos_filtered_by_duration_exact(self):
        response = self.client.get(
            "/polls/videos/recommendations/?metadata[duration]=10"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)

        response = self.client.get(
            "/polls/videos/recommendations/?metadata[duration::int]=10"
        )

        results = response.data["results"]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["metadata"]["duration"], 10)

    def test_anon_can_list_videos_filtered_by_duration_lt(self):
        response = self.client.get(
            "/polls/videos/recommendations/?metadata[duration:lt:int]=120"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["metadata"]["duration"], 10)

        response = self.client.get(
            "/polls/videos/recommendations/?metadata[duration:lte:int]=120"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data["results"]
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["metadata"]["duration"], 120)
        self.assertEqual(results[1]["metadata"]["duration"], 10)

    def test_anon_can_list_videos_filtered_by_duration_gt(self):
        response = self.client.get(
            "/polls/videos/recommendations/?metadata[duration:gt:int]=120"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["metadata"]["duration"], 240)

        response = self.client.get(
            "/polls/videos/recommendations/?metadata[duration:gte:int]=120"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data["results"]
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["metadata"]["duration"], 240)
        self.assertEqual(results[1]["metadata"]["duration"], 120)

    def test_anon_can_list_videos_filtered_by_duration_illegal(self):
        """
        The special string "__" must be forbidden in any metadata filter
        field.
        """
        response = self.client.get(
            "/polls/videos/recommendations/?metadata[duration__lte::int]=10"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_can_list_recommendations_with_score_mode(self):
        response = self.client.get(
            "/polls/videos/recommendations/?score_mode=all_equal&weights[reliability]=10&weights[importance]=10&weights[largely_recommended]=0"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data["results"]
        self.assertEqual(len(results), 3)

        self.assertEqual(results[0]["uid"], self.video_3.uid)
        self.assertEqual(results[0]["total_score"], 5.0)
        self.assertEqual(results[1]["uid"], self.video_4.uid)
        self.assertEqual(results[1]["total_score"], 4.0)
        self.assertEqual(results[2]["uid"], self.video_2.uid)
        self.assertEqual(results[2]["total_score"], -2.0)

    def test_can_list_recommendations_with_mehestan_default_weights(self):
        response = self.client.get(
            "/polls/videos/recommendations/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["results"]
        self.assertEqual(len(results), 3)


class PollsEntityTestCase(TestCase):
    """
    TestCase of the PollsEntityView API.
    """

    # users available in all tests
    _user = "username"

    # videos available in all tests
    _uid_01 = "yt:video_id_01"

    _non_existing_uid = "yt:_non_existing"
    _non_existing_poll = "_non_existing"

    def setUp(self):
        self.client = APIClient()

        self.video_1 = VideoFactory(
            uid="yt:video_id_01",
            tournesol_score=-2,
            rating_n_contributors=4,
            rating_n_ratings=8,
        )

        self.user = UserFactory(username=self._user)

    def test_auth_can_read(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f"/polls/videos/entities/{self.video_1.uid}")

        data = response.data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["tournesol_score"], -2)
        self.assertEqual(data["n_comparisons"], 8)
        self.assertEqual(data["n_contributors"], 4)
        self.assertIn("total_score", data)
        self.assertIn("criteria_scores", data)

    def test_anon_can_read(self):
        response = self.client.get(f"/polls/videos/entities/{self.video_1.uid}")

        data = response.data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["tournesol_score"], -2)
        self.assertEqual(data["n_comparisons"], 8)
        self.assertEqual(data["n_contributors"], 4)
        self.assertIn("total_score", data)
        self.assertIn("criteria_scores", data)

    def test_users_read_404_if_uid_doesnt_exist(self):
        # anonymous user
        response = self.client.get(f"/polls/videos/entities/{self._non_existing_uid}")
        self.assertEqual(response.status_code, 404)

        # authenticated user
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f"/polls/videos/entities/{self._non_existing_uid}")
        self.assertEqual(response.status_code, 404)

    def test_users_read_404_if_poll_doesnt_exist(self):
        # anonymous user
        response = self.client.get(
            f"/polls/{self._non_existing_poll}/entities/{self.video_1.uid}"
        )
        self.assertEqual(response.status_code, 404)

        # authenticated user
        self.client.force_authenticate(user=self.user)
        response = self.client.get(
            f"/polls/{self._non_existing_poll}/entities/{self.video_1.uid}"
        )
        self.assertEqual(response.status_code, 404)


class PollsCriteriaScoreDistributionTestCase(TestCase):
    """
    TestCase of the PollsCriteriaScoreDistributionView API.
    """

    def setUp(self):
        self.client = APIClient()
        self.poll_videos = Poll.default_poll()

        user1 = User.objects.create_user(username="user1", email="test1@example.test")
        user2 = User.objects.create_user(username="user2", email="test2@example.test")

        self.entity_public = EntityFactory()
        self.entity_private = EntityFactory()

        self.contributor_ratings_1 = ContributorRatingFactory(
            user=user1, entity=self.entity_public, is_public=True
        )
        self.contributor_ratings_2 = ContributorRatingFactory(
            user=user2, entity=self.entity_public, is_public=True
        )

        self.contributor_ratings_private_1 = ContributorRatingFactory(
            user=user1, entity=self.entity_private, is_public=False
        )
        self.contributor_ratings_private_2 = ContributorRatingFactory(
            user=user2, entity=self.entity_private, is_public=False
        )

    def test_basic_api_call_is_successfull(self):
        response = self.client.get(
            f"/polls/videos/entities/{self.entity_public.uid}/criteria_scores_distributions"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_basic_call_missing_entity(self):
        response = self.client.get(
            "/polls/videos/entities/XYZ/criteria_scores_distributions"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_one_criteria_score_should_have_base_distribution(self):
        ContributorRatingCriteriaScoreFactory(
            contributor_rating=self.contributor_ratings_1,
            criteria="reliability",
            score=0.2,
        )
        response = self.client.get(
            f"/polls/videos/entities/{self.entity_public.uid}/criteria_scores_distributions"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["criteria_scores_distributions"]), 1)
        self.assertEqual(
            response.data["criteria_scores_distributions"][0]["criteria"], "reliability"
        )
        # The sixth position are values between (0, 0.2) because
        # we use a 10 bins between (-1, 1)
        self.assertEqual(
            response.data["criteria_scores_distributions"][0]["distribution"][5], 1
        )

    def test_two_criteria_score_should_have_right_distribution(self):
        ContributorRatingCriteriaScoreFactory(
            contributor_rating=self.contributor_ratings_1,
            criteria="reliability",
            score=2,
        )
        ContributorRatingCriteriaScoreFactory(
            contributor_rating=self.contributor_ratings_2,
            criteria="reliability",
            score=85,
        )

        response = self.client.get(
            f"/polls/videos/entities/{self.entity_public.uid}/criteria_scores_distributions"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["criteria_scores_distributions"]), 1)
        self.assertEqual(
            response.data["criteria_scores_distributions"][0]["criteria"], "reliability"
        )
        # The sixth position are values between (0, 20) because
        # we use a 10 bins between (-100, 100)
        self.assertEqual(
            response.data["criteria_scores_distributions"][0]["distribution"][5], 1
        )
        # The 10th position are all values above 80 because we use a 10 bins between (-100, 100)
        self.assertEqual(
            response.data["criteria_scores_distributions"][0]["distribution"][9], 1
        )
        # Distribution is always in a range [-100,100]
        self.assertEqual(
            min(response.data["criteria_scores_distributions"][0]["bins"]), -100
        )
        self.assertEqual(
            max(response.data["criteria_scores_distributions"][0]["bins"]), 100
        )

    def test_no_private_criteria_ratings_should_be_in_distribution(self):
        ContributorRatingCriteriaScoreFactory(
            contributor_rating=self.contributor_ratings_private_1,
            criteria="better_habits",
            score=2,
        )
        ContributorRatingCriteriaScoreFactory(
            contributor_rating=self.contributor_ratings_private_2,
            criteria="reliability",
            score=6,
        )

        response = self.client.get(
            f"/polls/videos/entities/{self.entity_private.uid}/criteria_scores_distributions"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["criteria_scores_distributions"]), 0)

    def test_all_criteria_ratings_should_be_in_distribution(self):
        ContributorRatingCriteriaScoreFactory(
            contributor_rating=self.contributor_ratings_1,
            criteria="better_habits",
            score=2,
        )
        ContributorRatingCriteriaScoreFactory(
            contributor_rating=self.contributor_ratings_2,
            criteria="reliability",
            score=6,
        )

        response = self.client.get(
            f"/polls/videos/entities/{self.entity_public.uid}/criteria_scores_distributions"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["criteria_scores_distributions"]), 2)

    def test_value_in_minus_1_plus_1_should_have_default_bins(self):
        ContributorRatingCriteriaScoreFactory(
            contributor_rating=self.contributor_ratings_1,
            criteria="better_habits",
            score=0.6,
        )
        ContributorRatingCriteriaScoreFactory(
            contributor_rating=self.contributor_ratings_2,
            criteria="better_habits",
            score=-0.6,
        )

        response = self.client.get(
            f"/polls/videos/entities/{self.entity_public.uid}/criteria_scores_distributions"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["criteria_scores_distributions"]), 1)
        self.assertEqual(
            min(response.data["criteria_scores_distributions"][0]["bins"]), -100
        )
        self.assertEqual(
            max(response.data["criteria_scores_distributions"][0]["bins"]), 100
        )
