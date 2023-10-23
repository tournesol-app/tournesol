from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from core.tests.factories.user import UserFactory
from tournesol.lib.suggestions.strategies import ClassicEntitySuggestionStrategy
from tournesol.models import RateLater
from tournesol.tests.factories.entity import VideoFactory
from tournesol.tests.factories.entity_poll_rating import EntityPollRatingFactory
from tournesol.tests.factories.poll import PollWithCriteriasFactory
from tournesol.tests.factories.ratings import ContributorRatingCriteriaScoreFactory


class ClassicEntitySuggestionStrategyTestCase(TestCase):
    def setUp(self):
        self.user1 = UserFactory(username="username1")
        self.user2 = UserFactory(username="username2")

        self.poll1 = PollWithCriteriasFactory(entity_type="video")
        self.poll2 = PollWithCriteriasFactory(entity_type="video")

        self.strategy = ClassicEntitySuggestionStrategy(self.poll1, self.user1)

        today = timezone.now().date()

        self.recent_videos = VideoFactory.create_batch(
            20, metadata__publication_date=today.isoformat()
        )

        self.past_videos = VideoFactory.create_batch(
            20, metadata__publication_date=(today - timedelta(days=60)).isoformat()
        )

        self.videos = self.recent_videos + self.past_videos

    def test_ids_from_pool_compared(self):
        compared = self.strategy._ids_from_pool_compared()
        self.assertEqual(len(compared), 0)

        for count, video in enumerate(reversed(self.videos)):
            ContributorRatingCriteriaScoreFactory.create(
                score=(100 / len(self.videos)) * count,
                criteria=self.poll1.main_criteria,
                contributor_rating__poll=self.poll1,
                contributor_rating__entity=video,
                contributor_rating__user=self.user1,
            )

        compared = self.strategy._ids_from_pool_compared()
        self.assertEqual(len(compared), self.strategy.max_suggestions)
        self.assertTrue(set(compared).issubset(set(video.id for video in self.videos)))

    def test_ids_from_pool_rate_later(self):
        """
        The `_ids_from_pool_rate_later` method should return a random list of
        entity ids from the rate-later list defined by the pair
        `strategy.poll` / `strategy.user`.
        """
        results = self.strategy._ids_from_pool_rate_later([])
        self.assertEqual(len(results), 0)

        for i in range(20):
            RateLater.objects.create(poll=self.poll1, entity=self.videos[i], user=self.user1)

        # A second rate-later list with distinct entities ensures that all
        # entity ids are returned from the correct poll.
        for i in range(20, 40):
            RateLater.objects.create(poll=self.poll2, entity=self.videos[i], user=self.user1)

        # A third rate-later list with distinct entities ensures that all
        # entity ids are returned from the correct user's rate-later list.
        for i in range(20, 40):
            RateLater.objects.create(poll=self.poll1, entity=self.videos[i], user=self.user2)

        user1_rlater_list = RateLater.objects.filter(poll=self.poll1, user=self.user1).values_list(
            "entity_id", flat=True
        )

        user2_rlater_list = RateLater.objects.filter(poll=self.poll1, user=self.user2).values_list(
            "entity_id", flat=True
        )

        # 20 entity ids should be returned by default.
        results = self.strategy._ids_from_pool_rate_later([])
        self.assertEqual(len(results), 20)
        self.assertTrue(set(results).issubset(set(user1_rlater_list)))
        self.assertFalse(set(results).issubset(set(user2_rlater_list)))

        # The `exclude_ids` arg should exclude the provided entity ids.
        results = self.strategy._ids_from_pool_rate_later(exclude_ids=user1_rlater_list[:10])
        self.assertEqual(len(results), 10)
        self.assertTrue(set(results).issubset(set(user1_rlater_list)))
        self.assertFalse(set(results).issubset(set(user2_rlater_list)))

    def test_ids_from_pool_reco_last_month(self):
        """
        The `_ids_from_pool_reco_last_month` method should return a random
        list of entity ids from the last month recommendations.
        """
        results = self.strategy._ids_from_pool_reco_last_month([])
        self.assertEqual(len(results), 0)

        recent_entities = []

        for entity in self.recent_videos[:10]:
            recent_entities.append(
                EntityPollRatingFactory.create(
                    poll=self.poll1,
                    entity=entity,
                    # XXX use the settings
                    tournesol_score=99,
                    sum_trust_scores=99,
                ).entity_id
            )

        for entity in self.recent_videos[10:]:
            EntityPollRatingFactory.create(
                poll=self.poll1, entity=entity, tournesol_score=0, sum_trust_scores=0
            )

        results = self.strategy._ids_from_pool_reco_last_month([])
        self.assertEqual(len(results), 10)
        self.assertTrue(set(results).issubset(set(recent_entities)))

        # Excluded entity ids should not be returned.
        results = self.strategy._ids_from_pool_reco_last_month(recent_entities[:5])
        self.assertEqual(len(results), 5)
        self.assertTrue(set(results).issubset(set(recent_entities[5:])))

    def test_ids_from_pool_reco_all_time(self):
        pass

    def test_consolidate_results(self):
        pass

    def test_get_result_for_user_intermediate(self):
        pass
