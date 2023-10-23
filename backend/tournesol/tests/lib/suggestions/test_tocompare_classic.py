from datetime import timedelta

from django.conf import settings
from django.test import TestCase
from django.utils import timezone

from core.tests.factories.user import UserFactory
from tournesol.lib.suggestions.strategies import ClassicEntitySuggestionStrategy
from tournesol.lib.suggestions.strategies.tocompare.classic import IdPool
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

        self.videos_new = VideoFactory.create_batch(
            20, metadata__publication_date=today.isoformat()
        )

        self.videos_past = VideoFactory.create_batch(
            20, metadata__publication_date=(today - timedelta(days=60)).isoformat()
        )

        self.videos = self.videos_new + self.videos_past

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

        for entity in self.videos_new[:10]:
            recent_entities.append(
                EntityPollRatingFactory.create(
                    poll=self.poll1,
                    entity=entity,
                    tournesol_score=settings.RECOMMENDATIONS_MIN_TOURNESOL_SCORE + 1,
                    sum_trust_scores=settings.RECOMMENDATIONS_MIN_TRUST_SCORES + 1,
                ).entity_id
            )

        for entity in self.videos_new[10:]:
            EntityPollRatingFactory.create(
                poll=self.poll1, entity=entity, tournesol_score=-1, sum_trust_scores=0
            )

        for entity in self.videos_past:
            EntityPollRatingFactory.create(
                poll=self.poll1,
                entity=entity,
                tournesol_score=settings.RECOMMENDATIONS_MIN_TOURNESOL_SCORE + 1,
                sum_trust_scores=settings.RECOMMENDATIONS_MIN_TRUST_SCORES + 1,
            )

        results = self.strategy._ids_from_pool_reco_last_month([])
        self.assertEqual(len(results), 10)
        self.assertTrue(set(results).issubset(set(recent_entities)))

        # Excluded entity ids should not be returned.
        results = self.strategy._ids_from_pool_reco_last_month(recent_entities[:5])
        self.assertEqual(len(results), 5)
        self.assertTrue(set(results).issubset(set(recent_entities[5:])))

    def test_ids_from_pool_reco_all_time(self):
        """
        The `_ids_from_pool_reco_all_time` method should return a random
        list of entity ids from the last month recommendations.
        """
        results = self.strategy._ids_from_pool_reco_all_time([])
        self.assertEqual(len(results), 0)

        past_entities = []

        for entity in self.videos_past[:10]:
            past_entities.append(
                EntityPollRatingFactory.create(
                    poll=self.poll1,
                    entity=entity,
                    tournesol_score=settings.RECOMMENDATIONS_MIN_TOURNESOL_SCORE + 1,
                    sum_trust_scores=settings.RECOMMENDATIONS_MIN_TRUST_SCORES + 1,
                ).entity_id
            )

        for entity in self.videos_past[10:]:
            EntityPollRatingFactory.create(
                poll=self.poll1, entity=entity, tournesol_score=0, sum_trust_scores=0
            )

        for entity in self.videos_new:
            EntityPollRatingFactory.create(
                poll=self.poll1,
                entity=entity,
                tournesol_score=settings.RECOMMENDATIONS_MIN_TOURNESOL_SCORE + 1,
                sum_trust_scores=settings.RECOMMENDATIONS_MIN_TRUST_SCORES + 1,
            )

        results = self.strategy._ids_from_pool_reco_all_time([])
        self.assertEqual(len(results), 10)
        self.assertTrue(set(results).issubset(set(past_entities)))

        # Excluded entity ids should not be returned.
        results = self.strategy._ids_from_pool_reco_all_time(past_entities[:5])
        self.assertEqual(len(results), 5)
        self.assertTrue(set(results).issubset(set(past_entities[5:])))

    def test_consolidate_results(self):
        """
        The `_consolidate_results` should return list made of items from three
        pools.

        If one pool doesn't contain enough items, more items from the other
        pools should be used to compensate.
        """
        pool1 = list(range(100, 120))
        pool2 = list(range(200, 220))
        pool3 = list(range(300, 320))

        p1_sample_size = 9
        p2_sample_size = 7
        p3_sample_size = 4

        # [WHEN] all the pools contain enough items to create samples
        # of the expected size.
        results = self.strategy._consolidate_results(
            IdPool(pool1, p1_sample_size),
            IdPool(pool2, p2_sample_size),
            IdPool(pool3, p3_sample_size),
        )

        # [THEN] the final results should contain exactly p1_sample_size items
        # from the pool 1, p2_sample_size from the pool 2, etc.
        self.assertTrue(set(results[:9]).issubset(pool1))
        self.assertTrue(set(results[9:16]).issubset(pool2))
        self.assertTrue(set(results[16:]).issubset(pool3))

        # [WHEN] the pool 1 contains empty slots.
        results = self.strategy._consolidate_results(
            IdPool(pool1[:7], 9),
            IdPool(pool2, 7),
            IdPool(pool3, 4),
        )

        # [THEN] the pools 2 and 3 should each fill half of the empty slots.
        self.assertTrue(set(results[:7]).issubset(pool1))
        self.assertTrue(set(results[7:15]).issubset(pool2))
        self.assertTrue(set(results[15:]).issubset(pool3))

        # [WHEN] the pool 1 and 3 contain empty slots.
        results = self.strategy._consolidate_results(
            IdPool(pool1[:7], 9),
            IdPool(pool2, 7),
            IdPool(pool3[:2], 4),
        )

        # [THEN] the pool 2 should be able to fill all empty slots.
        self.assertTrue(set(results[:7]).issubset(pool1))
        self.assertTrue(set(results[7:18]).issubset(pool2))
        self.assertTrue(set(results[18:]).issubset(pool3))

        # [WHEN] the pool 1 and 2 contain empty slots.
        results = self.strategy._consolidate_results(
            IdPool(pool1[:7], 9),
            IdPool(pool2[:5], 7),
            IdPool(pool3, 4),
        )

        # [THEN] the pool 3 should be able to fill all empty slots.
        self.assertTrue(set(results[:7]).issubset(pool1))
        self.assertTrue(set(results[7:12]).issubset(pool2))
        self.assertTrue(set(results[12:]).issubset(pool3))


        # [WHEN] the pools 2 and 3 contain empty slots.
        results = self.strategy._consolidate_results(
            IdPool(pool1, 9),
            IdPool(pool2[:5], 7),
            IdPool(pool3[:2], 4),
        )

        # [THEN] the pool 1 should be able to fill all empty slots.
        self.assertTrue(set(results[:13]).issubset(pool1))
        self.assertTrue(set(results[13:18]).issubset(pool2))
        self.assertTrue(set(results[18:]).issubset(pool3))

    def test_get_result_for_user_intermediate(self):
        pass
