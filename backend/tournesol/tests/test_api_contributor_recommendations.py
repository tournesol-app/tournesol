from django.test import TestCase
from rest_framework.test import APIClient

from core.tests.factories.user import UserFactory
from tournesol.models import ContributorRating, ContributorRatingCriteriaScore, Poll
from tournesol.tests.factories.comparison import ComparisonFactory
from tournesol.tests.factories.entity import EntityFactory
from tournesol.tests.factories.poll import PollWithCriteriasFactory
from tournesol.tests.factories.ratings import (
    ContributorRatingCriteriaScoreFactory,
    ContributorRatingFactory,
)


class ContributorRecommendationsApiTestCase(TestCase):
    """
    TestCase of the Contributor Recommendations API.
    """

    def setUp(self):
        self.client = APIClient()

        self.poll = Poll.default_poll()
        self.criteria = self.poll.criterias_list[0]

        self.user1 = UserFactory()
        self.user2 = UserFactory()

        self.entity1 = EntityFactory(tournesol_score=1)
        self.entity2 = EntityFactory(tournesol_score=1)

        ContributorRatingFactory(user=self.user1, entity=self.entity1, is_public=True)
        ContributorRatingFactory(user=self.user1, entity=self.entity2, is_public=False)
        ContributorRatingFactory(user=self.user2, entity=self.entity1, is_public=True)
        ContributorRatingFactory(user=self.user2, entity=self.entity2, is_public=True)

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

        # Entities for which the score is 0 are filtered, so set a positive score
        ContributorRatingCriteriaScore.objects.bulk_create(
            [
                ContributorRatingCriteriaScore(
                    contributor_rating=contributor_rating,
                    criteria=self.criteria,
                    score=1,
                    uncertainty=0,
                )
                for contributor_rating in ContributorRating.objects.all()
            ]
        )

    def test_auth_can_list_private_recommendations(self):
        """An authenticated user can list its private recommendations."""
        self.client.force_authenticate(self.user1)
        initial_entity_nbr = ContributorRating.objects.filter(user=self.user1).count()

        response = self.client.get(
            f"/users/me/recommendations/{self.poll.name}", format="json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], initial_entity_nbr)

    def test_anon_cant_list_private_recommendations(self):
        """An anonymous user can't list its private recommendations."""
        response = self.client.get(
            f"/users/me/recommendations/{self.poll.name}", format="json"
        )
        self.assertEqual(response.status_code, 401)

    def test_recommendations_privacy_auth(self):
        """
        An authenticated user can only see public recommendations when using
        the public contributor recommendations endpoint.
        """
        self.client.force_authenticate(self.user1)

        response = self.client.get(
            f"/users/{self.user1.username}/recommendations/{self.poll.name}",
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)

        results = response.data["results"]
        for entity in results:
            self.assertEqual(entity["is_public"], True)

        # The collective metadata `n_comparisons` and `n_contributors` must
        # be present in the response of the public personal reco. endpoint.
        self.assertEqual(results[0]["n_comparisons"], 0)
        self.assertEqual(results[0]["n_contributors"], 0)

        response = self.client.get(
            f"/users/{self.user2.username}/recommendations/{self.poll.name}",
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 2)

        results = response.data["results"]
        for entity in results:
            self.assertEqual(entity["is_public"], True)

        # The collective metadata `n_comparisons` and `n_contributors` must
        # be present in the response of the public personal reco. endpoint.
        self.assertEqual(results[0]["n_comparisons"], 0)
        self.assertEqual(results[0]["n_contributors"], 0)

    def test_recommendations_privacy_anon(self):
        """
        An anonymous user can only see public recommendations when using
        the public contributor recommendations endpoint.
        """
        response = self.client.get(
            f"/users/{self.user1.username}/recommendations/{self.poll.name}",
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)

        for entity in response.data["results"]:
            self.assertEqual(entity["is_public"], True)

        response = self.client.get(
            f"/users/{self.user2.username}/recommendations/{self.poll.name}",
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 2)

        for entity in response.data["results"]:
            self.assertEqual(entity["is_public"], True)

    def test_recommendations_are_filtered_by_poll(self):
        new_poll = PollWithCriteriasFactory()

        self.client.force_authenticate(self.user1)
        response = self.client.get(
            f"/users/me/recommendations/{new_poll.name}", format="json"
        )

        self.assertEqual(response.status_code, 200)
        # no entity must be recommended in this poll
        self.assertEqual(response.data["count"], 0)

        rating = ContributorRatingFactory(
            poll=new_poll, user=self.user1, entity=self.entity1, is_public=True
        )
        ContributorRatingCriteriaScoreFactory(
            contributor_rating=rating, criteria=new_poll.criterias_list[0], score=1
        )

        response = self.client.get(
            f"/users/me/recommendations/{new_poll.name}", format="json"
        )
        # the private endpoint must return one recommendation
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)

        response = self.client.get(
            f"/users/{self.user1.username}/recommendations/{new_poll.name}",
            format="json",
        )
        # the public endpoint must return one recommendation
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)

    def test_users_cant_list_with_non_existing_user(self):
        """
        Anonymous and authenticated users can't list recommendations of a
        non-existing user.
        """
        response = self.client.get(
            f"/users/non-existing/recommendations/{self.poll.name}", format="json"
        )
        self.assertEqual(response.status_code, 404)

        self.client.force_authenticate(self.user1)
        response = self.client.get(
            f"/users/non-existing/recommendations/{self.poll.name}", format="json"
        )
        self.assertEqual(response.status_code, 404)

    def test_users_cant_list_with_non_existing_poll(self):
        """
        Anonymous and authenticated users can't list recommendations of a
        non-existing poll.
        """
        response = self.client.get(
            f"/users/{self.user1.username}/recommendations/non-existing", format="json"
        )
        self.assertEqual(response.status_code, 404)

        self.client.force_authenticate(self.user1)
        response = self.client.get(
            f"/users/{self.user1.username}/recommendations/non-existing", format="json"
        )
        self.assertEqual(response.status_code, 404)

    def test_users_can_list_with_param_unsafe(self):
        """
        Anonymous and authenticated users can filter recommendations with the
        `unsafe` URL parameter.
        """
        user = UserFactory()
        entity = EntityFactory(tournesol_score=-1)
        rating = ContributorRatingFactory(user=user, entity=entity, is_public=True)
        ContributorRatingCriteriaScoreFactory(
            contributor_rating=rating,
            criteria=self.criteria,
            score=-1,
        )

        # anonymous checks
        response = self.client.get(
            f"/users/{user.username}/recommendations/{self.poll.name}", format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 0)

        response = self.client.get(
            f"/users/{user.username}/recommendations/{self.poll.name}?unsafe=true",
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)

        # authenticated checks
        self.client.force_authenticate(self.user1)
        response = self.client.get(
            f"/users/{user.username}/recommendations/{self.poll.name}", format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 0)

        response = self.client.get(
            f"/users/{user.username}/recommendations/{self.poll.name}?unsafe=true",
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)

    def test_recommendations_score_results(self):
        user = UserFactory()
        self.client.force_authenticate(user)

        criteria_score = 1.8
        weight = 2

        entity = EntityFactory(tournesol_score=1)
        rating = ContributorRatingFactory(user=user, entity=entity, is_public=True)
        ContributorRatingCriteriaScoreFactory(
            contributor_rating=rating,
            criteria=self.criteria,
            score=criteria_score,
        )

        response = self.client.get(
            f"/users/me/recommendations/{self.poll.name}?weights%5B{self.criteria}%5D={weight}",
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            len(response.data["results"][0]["criteria_scores"]),
            1,
        )
        self.assertEqual(
            response.data["results"][0]["criteria_scores"][0]["score"],
            criteria_score,
        )
        self.assertEqual(
            response.data["results"][0]["total_score"], criteria_score * weight
        )

        # user2's score on this entity must not affect user1's recommendations
        rating2 = ContributorRatingFactory(
            user=self.user2, entity=entity, is_public=True
        )
        ContributorRatingCriteriaScoreFactory(
            contributor_rating=rating2,
            criteria=self.criteria,
            score=-5,
        )

        response = self.client.get(
            f"/users/me/recommendations/{self.poll.name}?weights%5B{self.criteria}%5D={weight}",
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            len(response.data["results"][0]["criteria_scores"]),
            1,
        )
        # It shouldn't have changed, other users' ratings are ignored
        self.assertEqual(
            response.data["results"][0]["criteria_scores"][0]["score"],
            criteria_score,
        )
        self.assertEqual(
            response.data["results"][0]["total_score"], criteria_score * weight
        )

    def test_recommendations_are_sorted_by_descending_total_score(self):
        user = UserFactory()
        scores = [1, -1, 5, 0.5, 0, 2]

        for score in scores:
            entity = EntityFactory(tournesol_score=1)
            rating = ContributorRatingFactory(user=user, entity=entity, is_public=True)
            ContributorRatingCriteriaScoreFactory(
                contributor_rating=rating,
                criteria=self.criteria,
                score=score,
            )

        response = self.client.get(
            f"/users/{user.username}/recommendations/{self.poll.name}", format="json"
        )

        # sorted: [1, -1, 5, 0.5, 0, 2] => [5, 2, 1, .5, 0, -1]
        expected_results = sorted(scores, reverse=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], len(expected_results))
        self.assertEqual([e['criteria_scores'][0]["score"] for e in response.data["results"]], expected_results)
