from datetime import timedelta

from django.conf import settings
from django.test import TestCase
from django.utils import timezone

from core.tests.factories.user import UserFactory
from tournesol.lib.suggestions.strategies import ClassicEntitySuggestionStrategy
from tournesol.lib.suggestions.strategies.tocompare.classic import IdPool
from tournesol.models import RateLater
from tournesol.tests.factories.comparison import ComparisonFactory
from tournesol.tests.factories.entity import VideoFactory
from tournesol.tests.factories.entity_poll_rating import EntityPollRatingFactory
from tournesol.tests.factories.poll import PollWithCriteriasFactory
from tournesol.tests.factories.ratings import ContributorRatingCriteriaScoreFactory


def create_entity_poll_ratings(poll, entities, recommended):
    ids = []

    scores = {
        "tournesol_score": settings.RECOMMENDATIONS_MIN_TOURNESOL_SCORE + 1,
        "sum_trust_scores": settings.RECOMMENDATIONS_MIN_TRUST_SCORES + 1,
    }

    if not recommended:
        scores["tournesol_score"] = settings.RECOMMENDATIONS_MIN_TOURNESOL_SCORE - 1
        scores["sum_trust_scores"] = settings.RECOMMENDATIONS_MIN_TRUST_SCORES - 1

    for entity in entities:
        ids.append(EntityPollRatingFactory.create(poll=poll, entity=entity, **scores).entity_id)
    return ids


def create_contributor_rating_criteria_scores(poll, user, entities):
    for entity in entities:
        ContributorRatingCriteriaScoreFactory.create(
            score=44,
            criteria=poll.main_criteria,
            contributor_rating__poll=poll,
            contributor_rating__entity=entity,
            contributor_rating__user=user,
        )


class ClassicEntitySuggestionStrategyTestCase(TestCase):
    def setUp(self):
        self.poll1 = PollWithCriteriasFactory(name="poll1", entity_type="video")
        self.poll2 = PollWithCriteriasFactory(name="poll2", entity_type="video")

        self.user1 = UserFactory(
            username="username1",
            settings={
                "poll1": {"rate_later__auto_remove": 4},
                "poll2": {"rate_later__auto_remove": 4},
            },
        )
        self.user2 = UserFactory(
            username="username2",
            settings={
                "poll1": {"rate_later__auto_remove": 4},
                "poll2": {"rate_later__auto_remove": 4},
            },
        )

        self.strategy = ClassicEntitySuggestionStrategy(self.poll1, self.user1)

        today = timezone.now().date()

        self.videos_new_es = VideoFactory.create_batch(
            5, metadata__language="es", metadata__publication_date=today.isoformat()
        )
        self.videos_new_fr = VideoFactory.create_batch(
            5, metadata__language="fr", metadata__publication_date=today.isoformat()
        )
        self.videos_new_it = VideoFactory.create_batch(
            10, metadata__language="it", metadata__publication_date=today.isoformat()
        )

        self.videos_past_es = VideoFactory.create_batch(
            5,
            metadata__language="es",
            metadata__publication_date=(today - timedelta(days=60)).isoformat(),
        )
        self.videos_past_fr = VideoFactory.create_batch(
            5,
            metadata__language="fr",
            metadata__publication_date=(today - timedelta(days=60)).isoformat(),
        )
        self.videos_past_it = VideoFactory.create_batch(
            10,
            metadata__language="it",
            metadata__publication_date=(today - timedelta(days=60)).isoformat(),
        )

        self.videos_new = self.videos_new_es + self.videos_new_fr + self.videos_new_it
        self.videos_past = self.videos_past_es + self.videos_past_fr + self.videos_past_it
        self.videos = self.videos_new + self.videos_past

    def test_get_recommendations(self):
        """
        The method `_get_recommendations` should return all ids of recommended
        entities, filtered according to the provided parameters.
        """
        results = self.strategy._get_recommendations({}, [])
        self.assertEqual(len(results), 0)

        recent_entities = []
        recent_entities.extend(create_entity_poll_ratings(self.poll1, self.videos_new[:10], True))
        recent_entities.extend(create_entity_poll_ratings(self.poll1, self.videos_new[10:], False))

        past_entities = []
        past_entities.extend(create_entity_poll_ratings(self.poll1, self.videos_past[:10], True))
        past_entities.extend(create_entity_poll_ratings(self.poll1, self.videos_past[10:], False))

        today = timezone.now().date()

        # [WHEN] no filters are used,
        # [THEN] ids of all recommended entities should be returned.
        results = self.strategy._get_recommendations({}, [])
        self.assertEqual(len(results), 20)
        self.assertTrue(set(results).issuperset(recent_entities[:10]))
        self.assertTrue(set(results).issuperset(past_entities[:10]))

        # [WHEN] the filter `excluded_ids` is provided,
        # [THEN] only ids of matching entities should be returned.
        results = self.strategy._get_recommendations(
            {
                f"{self.poll1.entity_cls.get_filter_date_field()}__gte": (
                    today - timedelta(days=1)
                ).isoformat()
            },
            [],
        )
        self.assertEqual(len(results), 10)
        self.assertTrue(set(results) == set(recent_entities[:10]))

        # [WHEN] the filter `excluded_ids` is provided,
        # [THEN] excluded entity ids should not be returned.
        results = self.strategy._get_recommendations({}, exclude_ids=recent_entities)
        self.assertEqual(len(results), 10)
        self.assertTrue(set(results) == set(past_entities[:10]))

    def test_get_compared_sufficiently(self):
        """
        The method `_get_compared_sufficiently` should return entity ids that
        have been compared more than the user's setting `rate_later__auto_remove`.
        """
        results = self.strategy._get_compared_sufficiently({})
        self.assertEqual(len(results), 0)

        create_contributor_rating_criteria_scores(self.poll1, self.user1, self.videos_new)
        create_contributor_rating_criteria_scores(self.poll1, self.user2, self.videos_new)
        create_contributor_rating_criteria_scores(self.poll2, self.user1, self.videos_past)

        # [WHEN] the contributor ratings exist, and comparisons have been made,
        # [THEN] no entity ids should be returned.
        results = self.strategy._get_compared_sufficiently({})
        self.assertEqual(len(results), 0)

        comparisons_batch_user1 = [
            # nb comparisons is equal to the user's setting rate_later__auto_remove
            dict(entity_1=self.videos_new[4], entity_2=self.videos_new[10]),
            dict(entity_1=self.videos_new[4], entity_2=self.videos_new[11]),
            dict(entity_1=self.videos_new[4], entity_2=self.videos_new[12]),
            dict(entity_1=self.videos_new[4], entity_2=self.videos_new[13]),
            # nb comparisons is superior to the user's setting rate_later__auto_remove
            dict(entity_1=self.videos_new[5], entity_2=self.videos_new[14]),
            dict(entity_1=self.videos_new[5], entity_2=self.videos_new[15]),
            dict(entity_1=self.videos_new[5], entity_2=self.videos_new[16]),
            dict(entity_1=self.videos_new[5], entity_2=self.videos_new[17]),
            dict(entity_1=self.videos_new[5], entity_2=self.videos_new[18]),
        ]

        for comp in comparisons_batch_user1:
            ComparisonFactory(poll=self.poll1, user=self.user1, **comp)

        # Ensure the returned entity ids match the user1 comparisons.
        comparisons_batch_user2 = [
            dict(entity_1=self.videos_new[0], entity_2=self.videos_new[10]),
            dict(entity_1=self.videos_new[0], entity_2=self.videos_new[11]),
            dict(entity_1=self.videos_new[0], entity_2=self.videos_new[12]),
            dict(entity_1=self.videos_new[0], entity_2=self.videos_new[13]),
        ]

        for comp in comparisons_batch_user2:
            ComparisonFactory(poll=self.poll1, user=self.user2, **comp)

        # [WHEN] some entities have been compared sufficiently by the user1,
        # [THEN] their entity ids should be returned.
        results = self.strategy._get_compared_sufficiently({})
        self.assertEqual(len(results), 2)
        self.assertIn(self.videos_new[4].id, results)
        self.assertIn(self.videos_new[5].id, results)

        self.user1.settings[self.poll1.name] = {"rate_later__auto_remove": 99}
        self.user1.save(update_fields=["settings"])

        # [WHEN] no entities have been compared sufficiently by the user1,
        # [THEN] no entity ids should be returned.
        results = self.strategy._get_compared_sufficiently({})
        self.assertEqual(len(results), 0)

    def test_ids_from_pool_compared(self):
        """
        The method `_ids_from_pool_compared` should return entity ids that
        have been compared at least one time by the user, but strictly less
        than the user's setting `rate_later__auto_remove`.
        """
        compared = self.strategy._ids_from_pool_compared()
        self.assertEqual(len(compared), 0)

        create_contributor_rating_criteria_scores(self.poll1, self.user1, self.videos_new)
        create_contributor_rating_criteria_scores(self.poll1, self.user2, self.videos_past)

        # [GIVEN] 9 entities with comparisons.
        # Their number of comparisons is inferior to the user's rate_later__auto_remove.
        comparisons_batch_user1 = [
            dict(entity_1=self.videos_new[1], entity_2=self.videos_new[10]),
            dict(entity_1=self.videos_new[2], entity_2=self.videos_new[11]),
            dict(entity_1=self.videos_new[2], entity_2=self.videos_new[12]),
            dict(entity_1=self.videos_new[3], entity_2=self.videos_new[13]),
            dict(entity_1=self.videos_new[3], entity_2=self.videos_new[14]),
            dict(entity_1=self.videos_new[3], entity_2=self.videos_new[15]),
        ]

        for comp in comparisons_batch_user1:
            ComparisonFactory(poll=self.poll1, user=self.user1, **comp)

        for i in range(len(self.videos_past)):
            ComparisonFactory(
                poll=self.poll1,
                user=self.user2,
                entity_1=self.videos_past[i],
                entity_2=self.videos_past[i - 1],
            )

        # [WHEN] the method `_ids_from_pool_compared` is called,
        # [THEN] all entity ids compared by the user1 should be returned.
        compared = self.strategy._ids_from_pool_compared()
        self.assertEqual(len(compared), 9)
        self.assertTrue(set(compared).issuperset(set([vid.id for vid in self.videos_new[1:4]])))
        self.assertTrue(set(compared).issuperset(set([vid.id for vid in self.videos_new[10:16]])))

        comparisons_batch_user1 = [
            dict(entity_1=self.videos_new[2], entity_2=self.videos_new[10]),
            dict(entity_1=self.videos_new[2], entity_2=self.videos_new[13]),
            dict(entity_1=self.videos_new[3], entity_2=self.videos_new[11]),
        ]

        for comp in comparisons_batch_user1:
            ComparisonFactory(poll=self.poll1, user=self.user1, **comp)

        # [WHEN] the method `_ids_from_pool_compared` is called,
        # [THEN] only entity ids that have been compared between 1 <= n < rate_later__auto_remove
        # times should be returned.
        compared = self.strategy._ids_from_pool_compared()
        self.assertEqual(len(compared), 7)
        self.assertTrue(set(compared).issuperset(set([self.videos_new[1].id])))
        self.assertTrue(set(compared).issuperset(set([vid.id for vid in self.videos_new[10:16]])))

        self.user1.settings[self.poll1.name] = {"rate_later__auto_remove": 2}
        self.user1.save(update_fields=["settings"])

        # [WHEN] the method `_ids_from_pool_compared` is called,
        # [THEN] only entity ids that have been compared between 1 <= n < 2
        # times should be returned.
        results = self.strategy._ids_from_pool_compared()
        self.assertEqual(len(results), 4)
        self.assertIn(self.videos_new[1].id, results)
        self.assertIn(self.videos_new[12].id, results)
        self.assertIn(self.videos_new[14].id, results)
        self.assertIn(self.videos_new[15].id, results)

    def test_ids_from_pool_rate_later(self):
        """
        The `_ids_from_pool_rate_later` method should return a random list of
        entity ids from the rate-later list defined by the pair
        `strategy.poll` / `strategy.user`.
        """
        results = self.strategy._ids_from_pool_rate_later([])
        self.assertEqual(len(results), 0)

        for vid in self.videos[:20]:
            RateLater.objects.create(poll=self.poll1, entity=vid, user=self.user1)

        # A second rate-later list with distinct entities ensures that all
        # entity ids are returned from the correct poll.
        for vid in self.videos[20:]:
            RateLater.objects.create(poll=self.poll2, entity=vid, user=self.user1)

        # A third rate-later list with distinct entities ensures that all
        # entity ids are returned from the correct user's rate-later list.
        for vid in self.videos[20:]:
            RateLater.objects.create(poll=self.poll1, entity=vid, user=self.user2)

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

        # [WHEN] the filter `excluded_ids` is provided,
        # [THEN] excluded entity ids should not be returned.
        results = self.strategy._ids_from_pool_rate_later(exclude_ids=user1_rlater_list[:10])
        self.assertEqual(len(results), 10)
        self.assertTrue(set(results).issubset(set(user1_rlater_list)))
        self.assertFalse(set(results).issubset(set(user2_rlater_list)))

    def test_ids_from_pool_reco_last_month(self):
        """
        The method `_ids_from_pool_reco_last_month` should return a random
        list of entity ids from the last month recommendations.
        """
        results = self.strategy._ids_from_pool_reco_last_month([])
        self.assertEqual(len(results), 0)

        recent_entities = []
        recent_entities.extend(create_entity_poll_ratings(self.poll1, self.videos_new[:10], True))
        create_entity_poll_ratings(self.poll1, self.videos_new[10:], False)
        create_entity_poll_ratings(self.poll1, self.videos_past[:10], True)

        # [WHEN] no filters are provided.
        # [THEN] only the recommended "recent" entities should be returned.
        results = self.strategy._ids_from_pool_reco_last_month([])
        self.assertEqual(len(results), 10)
        self.assertTrue(set(results) == set(recent_entities[:10]))

        # [WHEN] the filter `excluded_ids` is provided.
        # [THEN] excluded entity ids should not be returned.
        results = self.strategy._ids_from_pool_reco_last_month(recent_entities[:5])
        self.assertEqual(len(results), 5)
        self.assertTrue(set(results) == set(recent_entities[5:]))

    def test_ids_from_pool_reco_last_month_lang_filter(self):
        # [WHEN] the strategy is initialized with one language
        strategy = ClassicEntitySuggestionStrategy(self.poll1, self.user1, ["es"])
        results = strategy._ids_from_pool_reco_last_month([])
        self.assertEqual(len(results), 0)

        entities_es = create_entity_poll_ratings(self.poll1, self.videos_new_es, True)
        entities_fr = create_entity_poll_ratings(self.poll1, self.videos_new_fr, True)
        entities_it = create_entity_poll_ratings(self.poll1, self.videos_new_it[:5], True)
        create_entity_poll_ratings(self.poll1, self.videos_new_it[5:], False)
        create_entity_poll_ratings(self.poll1, self.videos_past, True)

        # [THEN] all recommended "recent" entities matching this language should be returned.
        results = strategy._ids_from_pool_reco_last_month([])
        self.assertEqual(len(results), 5)
        self.assertTrue(set(results) == set(entities_es))

        # [WHEN] the strategy is initialized with several languages
        strategy = ClassicEntitySuggestionStrategy(self.poll1, self.user1, ["it", "fr"])

        # [THEN] all recommended "recent" entities matching those languages should be returned.
        results = strategy._ids_from_pool_reco_last_month([])
        self.assertEqual(len(results), 10)
        self.assertTrue(set(results) == set(entities_fr + entities_it))

        # [WHEN] the strategy is initialized with no language
        strategy = ClassicEntitySuggestionStrategy(self.poll1, self.user1, [])

        # [THEN] all recommended "recent" entities should be returned.
        results = strategy._ids_from_pool_reco_last_month([])
        self.assertEqual(len(results), 15)
        self.assertTrue(set(results) == set(entities_es + entities_fr + entities_it))

        # [WHEN] the strategy is initialized with no language
        strategy = ClassicEntitySuggestionStrategy(self.poll1, self.user1, None)

        # [THEN] all recommended "recent" entities should be returned.
        results = strategy._ids_from_pool_reco_last_month([])
        self.assertEqual(len(results), 15)
        self.assertTrue(set(results) == set(entities_es + entities_fr + entities_it))

    def test_ids_from_pool_reco_all_time(self):
        """
        The method `_ids_from_pool_reco_all_time` should return a random
        list of entity ids from the last month recommendations.
        """
        results = self.strategy._ids_from_pool_reco_all_time([])
        self.assertEqual(len(results), 0)

        past_entities = []
        past_entities.extend(create_entity_poll_ratings(self.poll1, self.videos_past[:10], True))
        create_entity_poll_ratings(self.poll1, self.videos_past[10:], False)
        create_entity_poll_ratings(self.poll1, self.videos_new[:10], True)

        # [WHEN] no filters are provided.
        # [THEN] only the recommended "past" entities should be returned.
        results = self.strategy._ids_from_pool_reco_all_time([])
        self.assertEqual(len(results), 10)
        self.assertTrue(set(results) == set(past_entities[:10]))

        # [WHEN] the filter `excluded_ids` is provided.
        # [THEN] excluded entity ids should not be returned.
        results = self.strategy._ids_from_pool_reco_all_time(past_entities[:5])
        self.assertEqual(len(results), 5)
        self.assertTrue(set(results) == set(past_entities[5:]))

    def test_ids_from_pool_reco_all_time_lang_filter(self):
        # [WHEN] the strategy is initialized with one language
        strategy = ClassicEntitySuggestionStrategy(self.poll1, self.user1, ["es"])
        results = strategy._ids_from_pool_reco_all_time([])
        self.assertEqual(len(results), 0)

        entities_es = create_entity_poll_ratings(self.poll1, self.videos_past_es, True)
        entities_fr = create_entity_poll_ratings(self.poll1, self.videos_past_fr, True)
        entities_it = create_entity_poll_ratings(self.poll1, self.videos_past_it[:5], True)
        create_entity_poll_ratings(self.poll1, self.videos_past_it[5:], False)
        create_entity_poll_ratings(self.poll1, self.videos_new, True)

        # [THEN] all recommended "past" entities matching this language should be returned.
        results = strategy._ids_from_pool_reco_all_time([])
        self.assertEqual(len(results), 5)
        self.assertTrue(set(results) == set(entities_es))

        # [WHEN] the strategy is initialized with several languages
        strategy = ClassicEntitySuggestionStrategy(self.poll1, self.user1, ["it", "fr"])

        # [THEN] all recommended "past" entities matching those languages should be returned.
        results = strategy._ids_from_pool_reco_all_time([])
        self.assertEqual(len(results), 10)
        self.assertTrue(set(results) == set(entities_fr + entities_it))

        # [WHEN] the strategy is initialized with no language
        strategy = ClassicEntitySuggestionStrategy(self.poll1, self.user1, [])

        # [THEN] all recommended "past" entities should be returned.
        results = strategy._ids_from_pool_reco_all_time([])
        self.assertEqual(len(results), 15)
        self.assertTrue(set(results) == set(entities_es + entities_fr + entities_it))

        # [WHEN] the strategy is initialized with no language
        strategy = ClassicEntitySuggestionStrategy(self.poll1, self.user1, None)

        # [THEN] all recommended "past" entities should be returned.
        results = strategy._ids_from_pool_reco_all_time([])
        self.assertEqual(len(results), 15)
        self.assertTrue(set(results) == set(entities_es + entities_fr + entities_it))

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

        # [THEN] the pools 2 should fill the empty slots.
        self.assertTrue(set(results[:7]).issubset(pool1))
        self.assertTrue(set(results[7:16]).issubset(pool2))
        self.assertTrue(set(results[16:]).issubset(pool3))

        # [WHEN] the pool 2 contains empty slots.
        results = self.strategy._consolidate_results(
            IdPool(pool1, 9),
            IdPool(pool2[:5], 7),
            IdPool(pool3, 4),
        )

        # [THEN] the pool 1 should fill the empty slots.
        self.assertTrue(set(results[:11]).issubset(pool1))
        self.assertTrue(set(results[11:6]).issubset(pool2))
        self.assertTrue(set(results[16:]).issubset(pool3))

        # [WHEN] the pool 1 and 2 contain empty slots.
        results = self.strategy._consolidate_results(
            IdPool(pool1[:7], 9),
            IdPool(pool2[:5], 7),
            IdPool(pool3, 4),
        )

        # [THEN] the pool 3 should fill the empty slots.
        self.assertTrue(set(results[:7]).issubset(pool1))
        self.assertTrue(set(results[7:12]).issubset(pool2))
        self.assertTrue(set(results[12:]).issubset(pool3))

    def test_get_results_for_user_intermediate_only_compared(self):
        """
        When the user has 0 entity in his/her rate-later list, the slots
        dedicated to the rate-late list should be filled by compared entity
        ids.
        """
        results = self.strategy.get_results_for_user_intermediate()
        self.assertEqual(len(results), 0)

        create_contributor_rating_criteria_scores(self.poll1, self.user1, self.videos_new)
        comparisons_batch_user1 = []

        for i in range(20):
            comparisons_batch_user1.append(
                dict(entity_1=self.videos_new[i], entity_2=self.videos_new[i - 1])
            )

        for comp in comparisons_batch_user1:
            ComparisonFactory(poll=self.poll1, user=self.user1, **comp)

        results = self.strategy.get_results_for_user_intermediate()
        results_ids = [entity.id for entity in results]

        self.assertEqual(len(results), 16)
        self.assertTrue(set(results_ids).issubset([vid.id for vid in self.videos_new]))

        # The all-time recommendations always fill the remaining empty slots.
        create_entity_poll_ratings(self.poll1, self.videos_past, True)
        results = self.strategy.get_results_for_user_intermediate()

        results_ids = [entity.id for entity in results]
        results_compared = set(results_ids) & set([vid.id for vid in self.videos_new])
        results_alltime_reco = set(results_ids) & set([vid.id for vid in self.videos_past])

        self.assertEqual(len(results), 20)
        self.assertEqual(len(results_compared), 16)
        self.assertEqual(len(results_alltime_reco), 4)

    def test_get_results_for_user_intermediate_only_ratelater(self):
        """
        When 0 entities have been compared by the user, the slots dedicated to
        compared entities should be filled by ids from the user's rate-later
        list.
        """
        results = self.strategy.get_results_for_user_intermediate()
        self.assertEqual(len(results), 0)

        rate_later_id = []
        for vid in self.videos_new:
            rate_later_id.append(
                RateLater.objects.create(poll=self.poll1, entity=vid, user=self.user1).entity_id
            )

        results = self.strategy.get_results_for_user_intermediate()
        results_ids = [entity.id for entity in results]

        self.assertEqual(len(results), 16)
        self.assertTrue(set(results_ids).issubset(rate_later_id))

        # The all-time recommendations always fill the remaining empty slots.
        create_entity_poll_ratings(self.poll1, self.videos_past, True)
        results = self.strategy.get_results_for_user_intermediate()

        results_ids = [entity.id for entity in results]
        results_rate_later = set(results_ids) & set([vid.id for vid in self.videos_new])
        results_alltime_reco = set(results_ids) & set([vid.id for vid in self.videos_past])

        self.assertEqual(len(results), 20)
        self.assertEqual(len(results_rate_later), 16)
        self.assertEqual(len(results_alltime_reco), 4)

    def test_get_results_for_user_intermediate_only_reco_recent(self):
        """
        When the user has compared 0 entity and has 0 entity in his/her
        rate later-list, the recent and all-time recommendations should each
        fill half of the free slots.
        """
        results = self.strategy.get_results_for_user_intermediate()
        self.assertEqual(len(results), 0)

        create_entity_poll_ratings(self.poll1, self.videos_new, True)
        results = self.strategy.get_results_for_user_intermediate()
        results_ids = [entity.id for entity in results]

        self.assertEqual(len(results), 12)
        self.assertTrue(set(results_ids).issubset([vid.id for vid in self.videos_new]))

        # The all-time recommendations always fill the remaining empty slots.
        create_entity_poll_ratings(self.poll1, self.videos_past, True)
        results = self.strategy.get_results_for_user_intermediate()

        results_ids = [entity.id for entity in results]
        results_recent_reco = set(results_ids) & set([vid.id for vid in self.videos_new])
        results_alltime_reco = set(results_ids) & set([vid.id for vid in self.videos_past])

        self.assertEqual(len(results), 20)
        self.assertEqual(len(results_recent_reco), 12)
        self.assertEqual(len(results_alltime_reco), 8)

    def test_get_results_for_user_intermediate_only_reco_alltime(self):
        results = self.strategy.get_results_for_user_intermediate()
        self.assertEqual(len(results), 0)

        create_entity_poll_ratings(self.poll1, self.videos_past, True)
        results = self.strategy.get_results_for_user_intermediate()
        results_ids = [entity.id for entity in results]

        self.assertEqual(len(results), 20)
        self.assertTrue(set(results_ids).issubset([vid.id for vid in self.videos_past]))

    def test_get_results_for_user_intermediate(self):
        """
        The method `_get_result_for_user_intermediate` should return 9
        entities compared by the user, 7 from his/her rate-later list, and 4
        from the recent recommendations.
        """
        results = self.strategy.get_results_for_user_intermediate()
        self.assertEqual(len(results), 0)

        compared_entities = self.videos_past[:10]
        rate_later_entities = self.videos_past[10:]

        create_contributor_rating_criteria_scores(self.poll1, self.user1, compared_entities)
        comparisons_batch_user1 = []

        for i in range(10):
            comparisons_batch_user1.append(
                dict(entity_1=compared_entities[i], entity_2=compared_entities[i - 1])
            )

        for comp in comparisons_batch_user1:
            ComparisonFactory(poll=self.poll1, user=self.user1, **comp)

        rate_later_id = []
        for video in rate_later_entities:
            rate_later_id.append(
                RateLater.objects.create(poll=self.poll1, entity=video, user=self.user1).entity_id
            )

        create_entity_poll_ratings(self.poll1, self.videos_new, True)
        results = self.strategy.get_results_for_user_intermediate()
        results_ids = [entity.id for entity in results]

        self.assertEqual(len(results), 20)
        self.assertEqual(len(set(results_ids) & set([vid.id for vid in compared_entities])), 9)
        self.assertEqual(len(set(results_ids) & set([vid.id for vid in rate_later_entities])), 7)
        self.assertEqual(len(set(results_ids) & set([vid.id for vid in self.videos_new])), 4)
