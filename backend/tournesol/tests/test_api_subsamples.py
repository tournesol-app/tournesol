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

    user1_ratings_nb = 40
    user2_ratings_nb = 4

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

        results = response.data["results"]

        # By default, the API returns at most 20 rated entities from 20
        # different buckets.
        self.assertEqual(len(results), 20)

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

        results = response.data["results"]
        self.assertEqual(len(results), 4)

        # The results:
        #  - are ordered by score descending
        #  - only contains entities rated by the logged-in user
        for idx, item in enumerate(results):
            self.assertEqual(item["entity"]["uid"], self.poll1_videos2[idx].uid)
            self.assertIn("individual_rating", item)
            self.assertIn("collective_rating", item)
            self.assertEqual(item["subsample_metadata"]["bucket"], idx + 1)

    def test_param_ntile_lt_rated_entities(self):
        """
        An authenticated user can define the number of ranked bucket used by
        the API thanks to the parameter `ntile`

        The number of result is limited by this parameter, even if the `limit`
        parameter is explicitly greater.
        """
        self.client.force_authenticate(self.user1)
        response = self.client.get(self.base_subsamples_url, {"ntile": 10, "limit": 40})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data["results"]
        self.assertEqual(len(results), 10)
        self.assertEqual(response.data["count"], 10)

        for idx, item in enumerate(results):
            from_ = idx * 4
            to = from_ + 4
            self.assertIn(
                item["entity"]["uid"], [video.uid for video in self.poll1_videos1[from_:to]]
            )
            self.assertEqual(item["subsample_metadata"]["bucket"], idx + 1)

    def test_param_ntile_gt_rated_entities(self):
        """
        When the parameter `ntile` is greater than the number of rated
        entities, all rated entities are returned.
        """
        self.client.force_authenticate(self.user1)
        response = self.client.get(self.base_subsamples_url, {"ntile": 80, "limit": 80})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data["results"]
        self.assertEqual(len(results), 40)
        self.assertEqual(response.data["count"], 40)

        for idx, item in enumerate(results):
            self.assertEqual(item["entity"]["uid"], self.poll1_videos1[idx].uid)
            self.assertEqual(item["subsample_metadata"]["bucket"], idx + 1)

    def test_pagination(self):
        ntile = 20
        limit = 10
        offset = 10

        self.client.force_authenticate(self.user1)
        response = self.client.get(
            self.base_subsamples_url,
            {"ntile": ntile, "limit": limit, "offset": offset}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data["results"]
        self.assertEqual(len(results), limit)
        self.assertEqual(response.data["count"], ntile)

        for idx, item in enumerate(results):
            # 20 = user1_ratings_nb / ntile * offset
            from_ = 20 + idx * 2
            to = from_ + 2
            self.assertIn(
                item["entity"]["uid"], [video.uid for video in self.poll1_videos1[from_:to]]
            )
            self.assertEqual(item["subsample_metadata"]["bucket"], offset + idx + 1)
