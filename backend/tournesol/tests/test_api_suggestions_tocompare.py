from datetime import timedelta

from django.conf import settings
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from core.models import User
from core.tests.factories.user import UserFactory
from tournesol.models import Poll, RateLater
from tournesol.tests.factories.comparison import ComparisonFactory
from tournesol.tests.factories.entity import VideoFactory
from tournesol.tests.factories.poll import PollWithCriteriasFactory
from tournesol.tests.factories.ratings import ContributorRatingCriteriaScoreFactory


def create_comparisons(poll: Poll, user: User, entities):
    for entity in entities:
        ContributorRatingCriteriaScoreFactory.create(
            score=44,
            criteria=poll.main_criteria,
            contributor_rating__poll=poll,
            contributor_rating__entity=entity,
            contributor_rating__user=user,
        )

    for i in range(len(entities)):
        ComparisonFactory.create(
            poll=poll, user=user, entity_1=entities[i], entity_2=entities[i - 1]
        )


def update_entity_poll_rating(poll, entities, recommended, **kwargs):
    scores = {
        "tournesol_score": settings.RECOMMENDATIONS_MIN_TOURNESOL_SCORE + 1,
        "sum_trust_scores": settings.RECOMMENDATIONS_MIN_TRUST_SCORES + 1,
    }

    if not recommended:
        scores["tournesol_score"] = settings.RECOMMENDATIONS_MIN_TOURNESOL_SCORE - 1
        scores["sum_trust_scores"] = settings.RECOMMENDATIONS_MIN_TRUST_SCORES - 1

    for entity in entities:
        entity.all_poll_ratings.filter(poll=poll).update(**scores, **kwargs)


class SuggestionsToCompareTestCase(TestCase):
    _username1 = "username1"
    _username2 = "username2"

    def setUp(self):
        self.client = APIClient()

        # The main poll used by the tests.
        self.poll1 = PollWithCriteriasFactory.create()
        # This second poll allows to check if the API results are correctly
        # limited by poll.
        self.poll2 = PollWithCriteriasFactory.create()

        self.base_url = f"/users/me/suggestions/{self.poll1.name}/tocompare/"

        self.user1 = UserFactory(username=self._username1)
        self.user2 = UserFactory(username=self._username2)

    def test_authentication_required(self):
        """
        Anonymous users cannot be suggested videos to compare.
        """
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.force_authenticate(self.user1)
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_response_integrity_strategy_classic(self):
        """
        Authenticated users can be suggested videos to compare in the given
        poll.
        """
        compared_videos_user1_poll1 = VideoFactory.create_batch(9)
        compared_videos_user1_poll2 = VideoFactory.create_batch(9)
        compared_videos_user2_poll1 = VideoFactory.create_batch(9)

        create_comparisons(self.poll1, self.user1, compared_videos_user1_poll1)
        create_comparisons(self.poll2, self.user1, compared_videos_user1_poll2)
        create_comparisons(self.poll1, self.user2, compared_videos_user2_poll1)

        update_entity_poll_rating(
            self.poll1,
            compared_videos_user1_poll1,
            recommended=False,
            n_comparisons=11,
            n_contributors=33,
        )

        update_entity_poll_rating(
            self.poll2,
            compared_videos_user1_poll1,
            recommended=False,
            n_comparisons=22,
            n_contributors=44,
        )

        rate_later_videos_user1_poll1 = VideoFactory.create_batch(7)
        rate_later_videos_user1_poll2 = VideoFactory.create_batch(7)
        rate_later_videos_user2_poll1 = VideoFactory.create_batch(7)

        for i in range(7):
            RateLater.objects.create(
                poll=self.poll1, entity=rate_later_videos_user1_poll1[i], user=self.user1
            )
            RateLater.objects.create(
                poll=self.poll2, entity=rate_later_videos_user1_poll2[i], user=self.user1
            )
            RateLater.objects.create(
                poll=self.poll1, entity=rate_later_videos_user2_poll1[i], user=self.user2
            )

        today = timezone.now().date()
        recommendations_new = VideoFactory.create_batch(
            4,
            metadata__language="en",
            metadata__publication_date=today.isoformat(),
            make_safe_for_poll=self.poll1,
        )

        long_time_ago = timezone.now() - timedelta(days=120)
        recommendations_past = VideoFactory.create_batch(
            4,
            metadata__language="en",
            metadata__publication_date=long_time_ago.isoformat(),
            make_safe_for_poll=self.poll1,
        )

        self.client.force_authenticate(self.user1)
        response = self.client.get(self.base_url)
        results = response.data

        uids_compared = [ent.uid for ent in compared_videos_user1_poll1]
        uids_rate_later = [ent.uid for ent in rate_later_videos_user1_poll1]
        uids_recommendations_new = [ent.uid for ent in recommendations_new]
        uids_returned = [res["entity"]["uid"] for res in results]

        # The results match the pair user1 / poll1
        self.assertEqual(len(results), 20)
        self.assertIn("entity", results[0])

        videos_with_comparisons = [
            r["entity"]["uid"]
            for r in results
            if r["collective_rating"] and r["collective_rating"]["n_comparisons"] == 11
        ]
        videos_with_contributors = [
            r["entity"]["uid"]
            for r in results
            if r["collective_rating"] and r["collective_rating"]["n_contributors"] == 33
        ]

        self.assertEqual(len(videos_with_comparisons), 9)
        self.assertEqual(len(videos_with_contributors), 9)
        self.assertEqual(set(videos_with_comparisons), set(videos_with_contributors))
        self.assertTrue(set(uids_returned).issuperset(uids_compared))
        self.assertTrue(set(uids_returned).issuperset(uids_rate_later))
        self.assertTrue(set(uids_returned).issuperset(uids_recommendations_new))
