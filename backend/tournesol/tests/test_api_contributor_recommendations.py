from django.test import TestCase
from rest_framework.test import APIClient

from core.tests.factories.user import UserFactory
from tournesol.models import ContributorRating, ContributorRatingCriteriaScore, Poll
from tournesol.tests.factories.comparison import ComparisonFactory
from tournesol.tests.factories.poll import PollWithCriteriasFactory
from tournesol.tests.factories.ratings import (
    ContributorRatingCriteriaScoreFactory,
    ContributorRatingFactory,
)
from tournesol.tests.factories.entity import EntityFactory


class ContributorRecommendationsApi(TestCase):
    """
    TestCase of the Contributor Recommendations API.
    """

    def setUp(self):
        self.poll = Poll.default_poll()  # used by default in all factories
        self.criterion = self.poll.criterias_list[0]

        self.user1 = UserFactory()
        self.user2 = UserFactory()

        self.entity1 = EntityFactory()
        self.entity2 = EntityFactory()

        ComparisonFactory(
            user=self.user1,
            entity_1=self.entity1,
            entity_2=self.entity2,
        )
        ComparisonFactory(
            user=self.user2,
            entity_1=self.entity1,
            entity_2=self.entity2,
        )

        ContributorRatingFactory(user=self.user1, entity=self.entity1, is_public=True)
        ContributorRatingFactory(user=self.user1, entity=self.entity2, is_public=False)
        ContributorRatingFactory(user=self.user2, entity=self.entity1, is_public=True)
        ContributorRatingFactory(user=self.user2, entity=self.entity2, is_public=True)

        # Entities for which the score is 0 are filtered, so set a positive score
        ContributorRatingCriteriaScore.objects.bulk_create([
            ContributorRatingCriteriaScore(
                contributor_rating=contributor_rating,
                criteria=self.criterion,
                score=1,
                uncertainty=0,
            )
            for contributor_rating in ContributorRating.objects.all()
        ])


    def test_recommendations_privacy(self):
        client = APIClient()
        client.force_authenticate(self.user1)

        response = client.get(
            f"/users/{self.user1.username}/recommendations/{self.poll.name}",
            format="json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)  # only 1 public entity

        response = client.get(
            f"/users/me/recommendations/{self.poll.name}",
            format="json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 2)  # 1 public and 1 private entity

    def test_polls_filtering(self):
        client = APIClient()
        client.force_authenticate(self.user1)

        new_poll = PollWithCriteriasFactory()

        response = client.get(
            f"/users/me/recommendations/{new_poll.name}",
            format="json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 0)  # no entity registered on this poll

        rating = ContributorRatingFactory(poll=new_poll, user=self.user1,
                                          entity=self.entity1, is_public=True)
        ContributorRatingCriteriaScoreFactory(contributor_rating=rating,
                                              criteria=new_poll.criterias_list[0],
                                              score=1)

        response = client.get(
            f"/users/me/recommendations/{new_poll.name}",
            format="json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)


    def test_recommendations_invalid_url(self):
        client = APIClient()

        response = client.get(
            f"/users/missing_username/recommendations/{self.poll.name}",
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
        entity = EntityFactory()
        rating = ContributorRatingFactory(user=user, entity=entity, is_public=True)
        ContributorRatingCriteriaScoreFactory(
            contributor_rating=rating,
            criteria=self.criterion,
            score=-1,  # negative rating
        )

        response = client.get(
            f"/users/{user.username}/recommendations/{self.poll.name}",
            format="json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 0)

        response = client.get(
            f"/users/{user.username}/recommendations/{self.poll.name}?unsafe=true",
            format="json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)   # Included the negatively rated entity

    def test_recommendations_score_results(self):
        client = APIClient()
        user = UserFactory()
        client.force_authenticate(user)

        criterion_score = 1.8  # arbitrary
        weight = 2

        entity = EntityFactory()
        rating = ContributorRatingFactory(user=user, entity=entity, is_public=True)
        ContributorRatingCriteriaScoreFactory(
            contributor_rating=rating,
            criteria=self.criterion,
            score=criterion_score,
        )

        response = client.get(
            f"/users/me/recommendations/{self.poll.name}?weights%5B{self.criterion}%5D={weight}",
            format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(len(response.data["results"][0]["contributor_ratings"]), 1)
        self.assertEqual(len(response.data["results"][0]["contributor_ratings"]
                                          [0]["criteria_scores"]), 1)
        self.assertEqual(response.data["results"][0]["contributor_ratings"][0]
                                      ["criteria_scores"][0]["score"], criterion_score)
        self.assertEqual(response.data["results"][0]["total_score"], criterion_score * weight)

        # user2's score on this entity should not affect user1's recommendations
        rating2 = ContributorRatingFactory(user=self.user2, entity=entity, is_public=True)
        ContributorRatingCriteriaScoreFactory(
            contributor_rating=rating2,
            criteria=self.criterion,
            score=-5,
        )

        response = client.get(
            f"/users/me/recommendations/{self.poll.name}?weights%5B{self.criterion}%5D={weight}",
            format="json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(len(response.data["results"][0]["contributor_ratings"]), 1)
        self.assertEqual(len(response.data["results"][0]["contributor_ratings"]
                                          [0]["criteria_scores"]), 1)
        # It shouldn't have changed, other users' ratings are ignored
        self.assertEqual(response.data["results"][0]["contributor_ratings"][0]
                                      ["criteria_scores"][0]["score"], criterion_score)
        self.assertEqual(response.data["results"][0]["total_score"], criterion_score * weight)

    def test_recommendations_scores_filtering_and_ordering(self):
        client = APIClient()

        user = UserFactory()
        scores = [1, -1, 5, 0.5, 0, 2]
        score_to_entity = {}
        for score in scores:
            entity = EntityFactory()
            rating = ContributorRatingFactory(user=user, entity=entity, is_public=True)
            ContributorRatingCriteriaScoreFactory(
                contributor_rating=rating,
                criteria=self.criterion,
                score=score,
            )
            score_to_entity[score] = entity

        response = client.get(
            f"/users/{user.username}/recommendations/{self.poll.name}",
            format="json"
        )

        # filtered and sorted: [1, -1, 5, 0.5, 0, 2] => [5, 2, 1, .5]
        expected_results = [5, 2, 1, .5]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], len(expected_results))

        for i, score in enumerate(expected_results):
            self.assertEqual(response.data["results"][i]["uid"], score_to_entity[score].uid)
