from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from core.tests.factories.user import UserFactory
from tournesol.models import ContributorRating, ContributorRatingCriteriaScore
from tournesol.tests.factories.comparison import ComparisonFactory
from tournesol.tests.factories.poll import PollWithCriteriasFactory
from tournesol.tests.factories.ratings import (
    ContributorRatingCriteriaScoreFactory,
    ContributorRatingFactory,
)
from tournesol.tests.factories.video import VideoFactory


class UserRecommendationsApi(TestCase):
    """
    TestCase of the User Recommendations API.
    """

    def setUp(self):
        self.poll = PollWithCriteriasFactory()
        self.criterion = self.poll.criterias_list[0]

        self.user1 = UserFactory()
        self.user2 = UserFactory()

        self.video1 = VideoFactory()
        self.video2 = VideoFactory()

        ComparisonFactory(
            user=self.user1,
            entity_1=self.video1,
            entity_2=self.video2,
        )
        ComparisonFactory(
            user=self.user2,
            entity_1=self.video1,
            entity_2=self.video2,
        )

        ContributorRatingFactory(user=self.user1, entity=self.video1, is_public=True)
        ContributorRatingFactory(user=self.user1, entity=self.video2, is_public=False)
        ContributorRatingFactory(user=self.user2, entity=self.video1, is_public=True)
        ContributorRatingFactory(user=self.user2, entity=self.video2, is_public=True)

        # Videos for which the score is 0 are filtered, so set a positive score
        ContributorRatingCriteriaScore.objects.bulk_create([
            ContributorRatingCriteriaScore(
                contributor_rating=contributor_rating,
                criteria=self.criterion,
                score=1,
                uncertainty=0,
            )
            for contributor_rating in ContributorRating.objects.all()
        ])


    def test_recommendations_include_private(self):
        client = APIClient()
        client.force_authenticate(self.user1)

        response = client.get(
            "/users/me/recommendations/videos",
            format="json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)  # only 1 public video

        response = client.get(
            "/users/me/recommendations/videos?include_private=true",
            format="json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 2)  # 1 public and 1 private video

    def test_recommendations_privacy(self):
        client = APIClient()

        response = client.get(
            f"/users/{self.user1.username}/recommendations/videos",
            format="json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)  # 1 public video

        response = client.get(
            f"/users/{self.user1.username}/recommendations/videos?include_private=true",
            format="json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)  # other user's private video not included

    def test_recommendations_invalid_url(self):
        client = APIClient()

        response = client.get(
            "/users/missing_username/recommendations/videos",
            format="json"
        )

        self.assertEqual(response.status_code, 404)

        response = client.get(
            f"/users/{self.user1.username}/recommendations/invalid_poll",
            format="json"
        )

        self.assertEqual(response.status_code, 404)

    def test_recommendations_unsafe(self):
        client = APIClient()

        user = UserFactory()
        video = VideoFactory()
        rating = ContributorRatingFactory(user=user, entity=video, is_public=True)
        ContributorRatingCriteriaScoreFactory(
            contributor_rating=rating,
            criteria=self.criterion,
            score=-1,  # negative rating
        )

        response = client.get(
            f"/users/{user.username}/recommendations/videos",
            format="json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 0)

        response = client.get(
            f"/users/{user.username}/recommendations/videos?unsafe=true",
            format="json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)   # Included the negatively rated video

    def test_recommendations_score_results(self):
        client = APIClient()
        user = UserFactory()
        client.force_authenticate(user)

        criterion_score = 1.8  # arbitrary
        weight = 2

        video = VideoFactory()
        rating = ContributorRatingFactory(user=user, entity=video, is_public=True)
        ContributorRatingCriteriaScoreFactory(
            contributor_rating=rating,
            criteria=self.criterion,
            score=criterion_score,
        )

        response = client.get(
            f"/users/me/recommendations/videos?weights%5B{self.criterion}%5D={weight}",
            format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["contributorvideoratings"][0]
                                      ["criteria_scores"][0]["score"], criterion_score)
        self.assertEqual(response.data["results"][0]["total_score"], criterion_score * weight)

        # user2's score on this video should not affect user1's recommendations
        rating2 = ContributorRatingFactory(user=self.user2, entity=video, is_public=True)
        ContributorRatingCriteriaScoreFactory(
            contributor_rating=rating2,
            criteria=self.criterion,
            score=-5,
        )

        response = client.get(
            f"/users/me/recommendations/videos?weights%5B{self.criterion}%5D={weight}",
            format="json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        # It shouldn't have changed, other users' ratings are ignored
        self.assertEqual(response.data["results"][0]["contributorvideoratings"][0]
                                      ["criteria_scores"][0]["score"], criterion_score)
        self.assertEqual(response.data["results"][0]["total_score"], criterion_score * weight)

    def test_recommendations_scores_filtering_and_ordering(self):
        client = APIClient()

        user = UserFactory()
        scores = [1, -1, 5, 0.5, 0, 2]
        score_to_video = {}
        for score in scores:
            video = VideoFactory()
            rating = ContributorRatingFactory(user=user, entity=video, is_public=True)
            ContributorRatingCriteriaScoreFactory(
                contributor_rating=rating,
                criteria=self.criterion,
                score=score,
            )
            score_to_video[score] = video

        response = client.get(
            f"/users/{user.username}/recommendations/videos",
            format="json"
        )

        # filtered and sorted: [1, -1, 5, 0.5, 0, 2] => [5, 2, 1, .5]
        expected_results = [5, 2, 1, .5]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], len(expected_results))

        for i, score in enumerate(expected_results):
            self.assertEqual(response.data["results"][i]["uid"], score_to_video[score].uid)
