from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from core.models import User
from core.tests.factories.user import UserFactory
from tournesol.models import Poll
from tournesol.tests.factories.entity import VideoFactory
from tournesol.tests.factories.poll import PollWithCriteriasFactory
from tournesol.tests.factories.ratings import ContributorRatingCriteriaScoreFactory


class SubSamplesListTestCase(TestCase):
    _username1 = "username1"
    _username2 = "username2"
    _max_results = 20

    def _create_contributor_ratings(self, poll: Poll, user: User, amount: int):
        videos = VideoFactory.create_batch(amount)

        for count, video in enumerate(reversed(videos)):
            ContributorRatingCriteriaScoreFactory.create(
                score=(100 / amount) * count,
                criteria=poll.main_criteria,
                contributor_rating__poll=poll,
                contributor_rating__entity=video,
                contributor_rating__user=user,
            )

        return videos

    def setUp(self):
        self.client = APIClient()

        # The main poll used by the tests.
        self.poll1 = PollWithCriteriasFactory.create()
        # This second poll allows to check if the API results are correctly
        # limited by poll.
        self.extra_poll = PollWithCriteriasFactory.create()

        self.base_subsamples_url = f"/users/me/subsamples/{self.poll1.name}/"

        self.user1 = UserFactory(username=self._username1)
        self.user2 = UserFactory(username=self._username2)

        self.user1_ratings_nb = self._max_results * 2
        self.user2_ratings_nb = 4

        self.poll1_videos1 = self._create_contributor_ratings(
            self.poll1, self.user1, self.user1_ratings_nb
        )

        self.poll1_videos2 = self._create_contributor_ratings(
            self.poll1, self.user2, self.user2_ratings_nb
        )

        self._create_contributor_ratings(self.extra_poll, self.user1, self.user1_ratings_nb)

    def test_authentication_required(self):
        """
        Anonymous users cannot access their ratings' sub-samples.
        """
        response = self.client.get(self.base_subsamples_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.force_authenticate(self.user1)
        response = self.client.get(self.base_subsamples_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_response_integrity_user1(self):
        """
        An authenticated user can get a sub-sample of its compared entities,
        order by the individual score (descending) computed for the poll's
        main criterion.
        """
        self.client.force_authenticate(self.user1)
        response = self.client.get(self.base_subsamples_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data

        # The API returns at most 20 rated entities.
        self.assertEqual(len(results), self._max_results)

        # The results:
        #  - are ordered by score descending
        #  - only contains entities rated by the logged-in user
        for idx, item in enumerate(results):
            from_ = idx * 2
            to = from_ + 2
            self.assertIn(
                item["entity"]["uid"], [video.uid for video in self.poll1_videos1[from_:to]]
            )
            self.assertIn("individual_rating", item)
            self.assertIn("collective_rating", item)
            self.assertEqual(item["subsample_metadata"]["bucket"], idx + 1)

    def test_response_integrity_user2_few_ratings(self):
        """
        An authenticated user with less than 20 ratings, will get as many
        items as his/her number of ratings.
        """
        self.client.force_authenticate(self.user2)
        response = self.client.get(self.base_subsamples_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data

        # The API returns at most 20 rated entities.
        self.assertEqual(len(results), self.user2_ratings_nb)

        # The results:
        #  - are ordered by score descending
        #  - only contains entities rated by the logged-in user
        for idx, item in enumerate(results):
            self.assertEqual(item["entity"]["uid"], self.poll1_videos2[idx].uid)
            self.assertIn("individual_rating", item)
            self.assertIn("collective_rating", item)
            self.assertEqual(item["subsample_metadata"]["bucket"], idx + 1)
