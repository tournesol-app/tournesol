from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from tournesol.models import Poll
from core.models import User


from .factories.entity import VideoCriteriaScoreFactory, VideoFactory, EntityFactory
from .factories.ratings import ContributorRatingFactory, ContributorRatingCriteriaScoreFactory


class PollsApi(TestCase):
    def test_anonymous_can_read(self):
        """An anonymous user can read a poll with its translated criteria."""
        client = APIClient(HTTP_ACCEPT_LANGUAGE="fr")
        response = client.get("/polls/videos/")
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data["name"], "videos")
        self.assertEqual(len(response_data["criterias"]), 10)
        self.assertEqual(response_data["criterias"][0], {
            "name": "largely_recommended",
            "label": "Devrait être largement recommandé",
            "optional": False,
        })


class PollsRecommendationsApi(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.video_1 = VideoFactory(
            metadata__publication_date="2021-01-01",
            tournesol_score=1.1,
            rating_n_contributors=2,
        )
        self.video_2 = VideoFactory(
            metadata__publication_date="2021-01-02",
            tournesol_score=2.2,
            rating_n_contributors=3,
        )
        self.video_3 = VideoFactory(
            metadata__publication_date="2021-01-03",
            tournesol_score=3.3,
            rating_n_contributors=4,
        )
        self.video_4 = VideoFactory(
            metadata__publication_date="2021-01-04",
            tournesol_score=4.4,
            rating_n_contributors=5,
        )

        VideoCriteriaScoreFactory(entity=self.video_1, criteria="reliability", score=-0.1)
        VideoCriteriaScoreFactory(entity=self.video_2, criteria="reliability", score=0.2)
        VideoCriteriaScoreFactory(entity=self.video_3, criteria="importance", score=0.3)
        VideoCriteriaScoreFactory(entity=self.video_4, criteria="importance", score=0.4)

    def test_anonymous_can_list_recommendations(self):
        response = self.client.get("/polls/videos/recommendations/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data["results"]
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]["tournesol_score"], 4.4)
        self.assertEqual(results[1]["tournesol_score"], 3.3)
        self.assertEqual(results[2]["tournesol_score"], 2.2)

    def test_ignore_score_attached_to_another_poll(self):
        other_poll = Poll.objects.create(name="other")
        video_5 = VideoFactory(
            metadata__publication_date="2021-01-05",
            rating_n_contributors=6,
        )
        VideoCriteriaScoreFactory(poll=other_poll, entity=video_5,
                                  criteria="importance", score=0.5)
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
            [r["uid"] for r in resp.data["results"]],
            [self.video_4.uid, self.video_3.uid],
        )

        # Disable both reliability and importance
        resp = self.client.get(
            "/polls/videos/recommendations/?weights[reliability]=0&weights[importance]=0"
        )
        self.assertEqual([r["uid"] for r in resp.data["results"]], [])

        # More weight to reliability should change the order
        resp = self.client.get(
            "/polls/videos/recommendations/?weights[reliability]=100&weights[importance]=10"
        )
        self.assertEqual(
            [r["uid"] for r in resp.data["results"]],
            [self.video_2.uid, self.video_4.uid, self.video_3.uid],
        )


class EntityPollDistributorTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.poll_videos = Poll.default_poll()

        user1 = User.objects.create_user(username="user1", email="test1@example.test")
        user2 = User.objects.create_user(username="user2", email="test2@example.test")

        self.entity1 = EntityFactory()

        self.contributor_ratings_1 = ContributorRatingFactory(user=user1, entity=self.entity1)
        self.contributor_ratings_2 = ContributorRatingFactory(user=user2, entity=self.entity1)

    def test_basic_api_call_is_successfull(self):
        response = self.client.get(
            f"/polls/videos/entities/{self.entity1.uid}/criteria_scores_distributions")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_one_criteria_score_should_have_base_distribution(self):
        ContributorRatingCriteriaScoreFactory(
            contributor_rating=self.contributor_ratings_1, criteria="reliability", score=5)
        response = self.client.get(
            f"/polls/videos/entities/{self.entity1.uid}/criteria_scores_distributions")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["criteria_scores_distributions"]), 1)
        self.assertEqual(response.data["criteria_scores_distributions"]
                         [0]["criteria"], "reliability")
        self.assertEqual(response.data["criteria_scores_distributions"][0]["distribution"][5], 1)

    def test_two_criteria_score_should_have_right_distribution(self):
        ContributorRatingCriteriaScoreFactory(
            contributor_rating=self.contributor_ratings_1, criteria="reliability", score=2)
        ContributorRatingCriteriaScoreFactory(
            contributor_rating=self.contributor_ratings_2, criteria="reliability", score=6)

        response = self.client.get(
            f"/polls/videos/entities/{self.entity1.uid}/criteria_scores_distributions")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["criteria_scores_distributions"]), 1)
        self.assertEqual(response.data["criteria_scores_distributions"]
                         [0]["criteria"], "reliability")
        self.assertEqual(response.data["criteria_scores_distributions"][0]["distribution"][0], 1)
        self.assertEqual(response.data["criteria_scores_distributions"][0]["distribution"][9], 1)
        self.assertEqual(min(response.data["criteria_scores_distributions"][0]["bins"]), 2)
        self.assertEqual(max(response.data["criteria_scores_distributions"][0]["bins"]), 6)

    def test_all_criteria_ratings_should_be_in_distribution(self):
        ContributorRatingCriteriaScoreFactory(
            contributor_rating=self.contributor_ratings_1, criteria="better_habits", score=2)
        ContributorRatingCriteriaScoreFactory(
            contributor_rating=self.contributor_ratings_2, criteria="reliability", score=6)

        response = self.client.get(
            f"/polls/videos/entities/{self.entity1.uid}/criteria_scores_distributions")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["criteria_scores_distributions"]), 2)
