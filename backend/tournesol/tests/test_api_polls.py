from datetime import timedelta

from django.core.cache import cache
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from core.models import User
from tournesol.models import Poll
from tournesol.models.entity_context import EntityContext, EntityContextLocale
from tournesol.tests.factories.comparison import ComparisonFactory
from tournesol.tests.factories.entity import (
    EntityFactory,
    UserFactory,
    VideoCriteriaScoreFactory,
    VideoFactory,
)
from tournesol.tests.factories.entity_poll_rating import EntityPollRatingFactory
from tournesol.tests.factories.ratings import (
    ContributorRatingCriteriaScoreFactory,
    ContributorRatingFactory,
)


class PollsTestCase(TestCase):
    """
    TestCase of the PollsView API.
    """

    @override_settings(
        # Use dummy cache to disable throttling when counting db queries
        CACHES={"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}}
    )
    def test_anonymous_can_read(self):
        """An anonymous user can read a poll with its translated criteria."""
        client = APIClient(HTTP_ACCEPT_LANGUAGE="fr")

        with self.assertNumQueries(3):
            response = client.get("/polls/videos/")

        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data["name"], "videos")
        self.assertEqual(response_data["active"], True)
        self.assertEqual(response_data["entity_type"], "video")
        self.assertEqual(len(response_data["criterias"]), 10)
        self.assertEqual(
            response_data["criterias"][0],
            {
                "name": "largely_recommended",
                "label": "Devrait être largement recommandé",
                "optional": False,
            },
        )


class PollsRecommendationsTestCase(TestCase):
    """
    TestCase of the PollsRecommendationsView API.
    """

    def setUp(self):
        self.client = APIClient()
        self.poll = Poll.default_poll()

        self.video_1 = VideoFactory(
            metadata__publication_date="2021-01-01",
            metadata__uploader="_test_uploader_1",
            metadata__language="es",
            tournesol_score=-1,
            make_safe_for_poll=False,
        )
        self.video_2 = VideoFactory(
            metadata__publication_date="2021-01-02",
            metadata__uploader="_test_uploader_2",
            metadata__language="fr",
            metadata__duration=10,
            tournesol_score=22,
            make_safe_for_poll=False,
        )
        self.video_3 = VideoFactory(
            metadata__publication_date="2021-01-03",
            metadata__uploader="_test_uploader_2",
            metadata__language="pt",
            metadata__duration=120,
            tournesol_score=33,
            make_safe_for_poll=False,
        )
        self.video_4 = VideoFactory(
            metadata__publication_date="2021-01-04",
            metadata__uploader="_test_uploader_3",
            metadata__language="it",
            metadata__duration=240,
            tournesol_score=44,
            make_safe_for_poll=False,
        )

        VideoCriteriaScoreFactory(
            entity=self.video_1, criteria="reliability", score=-0.1
        )
        VideoCriteriaScoreFactory(
            entity=self.video_2, criteria="reliability", score=0.2
        )
        VideoCriteriaScoreFactory(entity=self.video_3, criteria="importance", score=0.3)
        VideoCriteriaScoreFactory(entity=self.video_4, criteria="importance", score=0.4)

        VideoCriteriaScoreFactory(
            entity=self.video_1,
            criteria="reliability",
            score=0.1,
            score_mode="all_equal",
        )
        VideoCriteriaScoreFactory(
            entity=self.video_2,
            criteria="reliability",
            score=-0.2,
            score_mode="all_equal",
        )
        VideoCriteriaScoreFactory(
            entity=self.video_3,
            criteria="importance",
            score=0.5,
            score_mode="all_equal",
        )
        VideoCriteriaScoreFactory(
            entity=self.video_4,
            criteria="importance",
            score=0.4,
            score_mode="all_equal",
        )

    def test_anon_can_list_recommendations(self):
        response = self.client.get("/polls/videos/recommendations/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data["results"]
        self.assertEqual(len(results), 3)

        self.assertEqual(results[0]["collective_rating"]["tournesol_score"], 44.0)
        self.assertEqual(results[1]["collective_rating"]["tournesol_score"], 33.0)
        self.assertEqual(results[2]["collective_rating"]["tournesol_score"], 22.0)
        self.assertEqual(results[0]["entity"]["type"], "video")

        for result in results:
            self.assertEqual(result["entity_contexts"], [])

    def test_anon_can_list_reco_with_contexts(self):
        # An entity with an unsafe rating shouldn't be marked as safe by a context.
        EntityContext.objects.create(
            name="context_video1",
            origin=EntityContext.ASSOCIATION,
            predicate={"video_id": self.video_1.metadata["video_id"]},
            unsafe=False,
            enabled=True,
            poll=self.poll,
        )

        # An entity with at least one unsafe context should be marked as unsafe.
        EntityContext.objects.create(
            name="context_video2_unsafe",
            origin=EntityContext.ASSOCIATION,
            predicate={"video_id": self.video_2.metadata["video_id"]},
            unsafe=True,
            enabled=True,
            poll=self.poll,
        )

        EntityContext.objects.create(
            name="context_video2_safe",
            origin=EntityContext.ASSOCIATION,
            predicate={"video_id": self.video_2.metadata["video_id"]},
            unsafe=False,
            enabled=True,
            poll=self.poll,
        )

        # An entity with disabled unsafe contexts shouldn't be marked unsafe.
        EntityContext.objects.create(
            name="context_video3_1_unsafe_disabled",
            origin=EntityContext.ASSOCIATION,
            predicate={"video_id": self.video_3.metadata["video_id"]},
            unsafe=True,
            enabled=False,
            poll=self.poll,
        )

        context3_2 = EntityContext.objects.create(
            name="context_video3_2_unsafe_disabled",
            origin=EntityContext.ASSOCIATION,
            predicate={"video_id": self.video_3.metadata["video_id"]},
            unsafe=False,
            enabled=True,
            poll=self.poll,
        )

        context3_2_text = EntityContextLocale.objects.create(
            context=context3_2,
            language="en",
            text="Hello context3_2",
        )

        # An entity can have several contexts.
        context4_1 = EntityContext.objects.create(
            name="context_video4_1_safe",
            origin=EntityContext.ASSOCIATION,
            predicate={"video_id": self.video_4.metadata["video_id"]},
            unsafe=False,
            enabled=True,
            created_at=timezone.now() - timedelta(days=1),
            poll=self.poll,
        )

        context4_1_text = EntityContextLocale.objects.create(
            context=context4_1,
            language="en",
            text="Hello context4_1",
        )

        context4_2 = EntityContext.objects.create(
            name="context_video4_2_safe",
            origin=EntityContext.ASSOCIATION,
            predicate={"video_id": self.video_4.metadata["video_id"]},
            unsafe=False,
            enabled=True,
            created_at=timezone.now(),
            poll=self.poll,
        )

        context4_2_text = EntityContextLocale.objects.create(
            context=context4_2,
            language="en",
            text="Hello context4_2",
        )

        response = self.client.get("/polls/videos/recommendations/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data["results"]
        self.assertEqual(len(results), 2)

        self.assertEqual(len(results[0]["entity_contexts"]), 2)
        self.assertDictEqual(
            results[0]["entity_contexts"][0],
            {
                'origin': 'ASSOCIATION',
                'unsafe': False,
                'text': context4_2_text.text,
                'created_at': context4_2.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            }
        )
        self.assertDictEqual(
            results[0]["entity_contexts"][1],
            {
                'origin': 'ASSOCIATION',
                'unsafe': False,
                'text': context4_1_text.text,
                'created_at': context4_1.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            }
        )

        self.assertEqual(len(results[1]["entity_contexts"]), 1)
        self.assertDictEqual(
            results[1]["entity_contexts"][0],
            {
                'origin': 'ASSOCIATION',
                'unsafe': False,
                'text': context3_2_text.text,
                'created_at': context3_2.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            }
        )

    def test_anon_can_list_reco_with_contexts_unsafe(self):
        """
        Recommendations marked as unsafe by their context should be returned
        when the query parameter `unsafe` is used.
        """
        response = self.client.get("/polls/videos/recommendations/")
        initial_safe_results_nbr = len(response.data["results"])

        EntityContext.objects.create(
            name="context_video4_unsafe",
            origin=EntityContext.ASSOCIATION,
            predicate={"video_id": self.video_4.metadata["video_id"]},
            unsafe=True,
            enabled=True,
            poll=self.poll,
        )

        cache.clear()
        response = self.client.get("/polls/videos/recommendations/")
        results = response.data["results"]

        self.assertEqual(len(results), initial_safe_results_nbr - 1)
        self.assertNotIn(self.video_4.uid, [res["entity"]["uid"] for res in results])

        response = self.client.get("/polls/videos/recommendations/?unsafe=true")
        vid4 = response.data["results"][0]

        self.assertEqual(vid4["entity"]["uid"], self.video_4.uid)
        self.assertEqual(vid4["collective_rating"]["unsafe"]["status"], True)
        self.assertEqual(len(vid4["collective_rating"]["unsafe"]["reasons"]), 1)
        self.assertEqual(
            vid4["collective_rating"]["unsafe"]["reasons"][0],
            'moderation_by_association'
        )

    def test_anon_can_list_reco_with_contexts_poll_specific(self):
        """
        Only contexts related to the poll provided in the URL should be
        returned.
        """
        response = self.client.get("/polls/videos/recommendations/")
        initial_safe_results_nbr = len(response.data["results"])
        self.assertEqual(response.data["results"][0]["entity"]["uid"], self.video_4.uid)

        other_poll = Poll.objects.create(name="other")
        EntityContext.objects.create(
            name="context_video4_safe",
            origin=EntityContext.ASSOCIATION,
            predicate={"video_id": self.video_4.metadata["video_id"]},
            unsafe=False,
            enabled=True,
            poll=other_poll,
        )

        EntityContext.objects.create(
            name="context_video4_unsafe",
            origin=EntityContext.ASSOCIATION,
            predicate={"video_id": self.video_4.metadata["video_id"]},
            unsafe=True,
            enabled=True,
            poll=other_poll,
        )

        cache.clear()
        response = self.client.get("/polls/videos/recommendations/")
        results = response.data["results"]

        self.assertEqual(len(results), initial_safe_results_nbr)
        self.assertEqual(response.data["results"][0]["entity"]["uid"], self.video_4.uid)
        self.assertEqual(response.data["results"][0]["entity_contexts"], [])

    def test_ignore_score_attached_to_another_poll(self):
        other_poll = Poll.objects.create(name="other")
        video_5 = VideoFactory(
            metadata__publication_date="2021-01-05",
            n_contributors=6,
        )
        VideoCriteriaScoreFactory(
            poll=other_poll, entity=video_5, criteria="importance", score=0.5
        )
        response = self.client.get("/polls/videos/recommendations/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 3)

    def test_anon_can_list_unsafe_recommendations(self):
        response = self.client.get("/polls/videos/recommendations/?unsafe=true")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 4)
        self.assertEqual(
            response.data["results"][0]["collective_rating"]["unsafe"], {
                "status": False,
                "reasons": [],
            }
        )
        self.assertEqual(
            response.data["results"][3]["collective_rating"]["unsafe"], {
                "status": True,
                "reasons": ["insufficient_tournesol_score"],
            }
        )

    def test_anon_can_list_with_limit(self):
        """
        An anonymous user can list a subset of recommendations by using the
        `limit` query parameter.
        """
        response = self.client.get("/polls/videos/recommendations/?limit=1")
        results = response.data["results"]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(results[0]["collective_rating"]["tournesol_score"], 44.0)

        response = self.client.get("/polls/videos/recommendations/?limit=2")
        results = response.data["results"]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)
        self.assertEqual(results[0]["collective_rating"]["tournesol_score"], 44.0)
        self.assertEqual(results[1]["collective_rating"]["tournesol_score"], 33.0)

    def test_anon_can_list_with_offset(self):
        """
        An anonymous user can list a subset of recommendations by using the
        `offset` query parameter.
        """
        response = self.client.get("/polls/videos/recommendations/?offset=2")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_list_videos_with_criteria_weights(self):
        # Default weights: all criterias contribute equally
        resp = self.client.get("/polls/videos/recommendations/")
        self.assertEqual(
            [r["entity"]["uid"] for r in resp.data["results"]],
            [self.video_4.uid, self.video_3.uid, self.video_2.uid],
        )

        # Disable reliability
        resp = self.client.get("/polls/videos/recommendations/?weights[reliability]=0")
        self.assertEqual(
            # Only verifying the first two videos of the response because other videos
            # have only criteria scores for reliability
            [r["entity"]["uid"] for r in resp.data["results"]][:2],
            [self.video_4.uid, self.video_3.uid],
        )

        # Disable both reliability and importance
        resp = self.client.get(
            "/polls/videos/recommendations/?weights[reliability]=0&weights[importance]=0"
        )
        self.assertEqual(len(resp.data["results"]), 3)

        # Disable both reliability and importance and specify unsafe
        resp = self.client.get(
            "/polls/videos/recommendations/?weights[reliability]=0&weights[importance]=0&unsafe=true"
        )
        self.assertEqual(len(resp.data["results"]), 4)

        # More weight to reliability should change the order
        resp = self.client.get(
            "/polls/videos/recommendations/?weights[reliability]=100&weights[importance]=10"
        )
        self.assertEqual(
            [r["entity"]["uid"] for r in resp.data["results"]],
            [self.video_2.uid, self.video_4.uid, self.video_3.uid],
        )

    def test_anon_can_list_videos_filtered_by_metadata_single(self):
        """
        Anonymous users can filter the recommended videos using a single
        value filter.
        """
        resp = self.client.get(
            "/polls/videos/recommendations/?metadata[uploader]=_test_uploader_2"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [video["entity"]["uid"] for video in resp.data["results"]],
            [self.video_3.uid, self.video_2.uid],
        )

        resp = self.client.get(
            "/polls/videos/recommendations/?metadata[uploader]=_test_uploader_3"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["results"][0]["entity"]["uid"], self.video_4.uid)

        # filtering by an unknown single value metadata must return an empty list
        resp = self.client.get(
            "/polls/videos/recommendations/?metadata[uploader]=unknown_uploader"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["count"], 0)
        self.assertEqual(resp.data["results"], [])

    def test_anon_can_list_videos_filtered_by_metadata_multiple(self):
        """
        Anonymous users can filter the recommended videos using a multiple
        values filter.
        """
        resp = self.client.get("/polls/videos/recommendations/?metadata[language]=fr")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["results"][0]["entity"]["uid"], self.video_2.uid)

        resp = self.client.get(
            "/polls/videos/recommendations/?metadata[language]=fr"
            "&metadata[language]=pt"
            "&metadata[language]=it"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [video["entity"]["uid"] for video in resp.data["results"]],
            [self.video_4.uid, self.video_3.uid, self.video_2.uid],
        )

    def test_anon_can_list_videos_filtered_by_metadata_mixed(self):
        """
        Anonymous users can filter the recommended videos using a combination
        of single value and multiple values metadata filters.
        """
        resp = self.client.get(
            "/polls/videos/recommendations/?metadata[uploader]=_test_uploader_2"
            "&metadata[language]=fr&metadata[language]=pt&metadata[language]=it"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [video["entity"]["uid"] for video in resp.data["results"]],
            [self.video_3.uid, self.video_2.uid],
        )

        resp = self.client.get(
            "/polls/videos/recommendations/?metadata[uploader]=unknown_uploader"
            "&metadata[language]=fr&metadata[language]=pt&metadata[language]=it"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["count"], 0)
        self.assertEqual(resp.data["results"], [])

    def test_anon_can_list_videos_filtered_by_date(self):
        response = self.client.get(
            "/polls/videos/recommendations/?date_lte=2021-01-03T00:00:00.000Z"
        )
        results = response.data["results"]

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["entity"]["uid"], self.video_3.uid)
        self.assertEqual(results[1]["entity"]["uid"], self.video_2.uid)

        response = self.client.get(
            "/polls/videos/recommendations/?date_gte=2021-01-03T00:00:00.000Z"
        )
        results = response.data["results"]

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["entity"]["uid"], self.video_4.uid)

    def test_anon_cannot_use_forbidden_strings_in_metadata_filter(self):
        response = self.client.get("/polls/videos/recommendations/?metadata[__]=10")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.get(
            "/polls/videos/recommendations/?metadata[duration__lte]=10"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.get(
            "/polls/videos/recommendations/?metadata[duration__lte::int]=10"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_anon_can_list_videos_filtered_by_duration_exact(self):
        response = self.client.get(
            "/polls/videos/recommendations/?metadata[duration]=10"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)

        response = self.client.get(
            "/polls/videos/recommendations/?metadata[duration::int]=10"
        )

        results = response.data["results"]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["entity"]["metadata"]["duration"], 10)

    def test_anon_can_list_videos_filtered_by_duration_lt(self):
        response = self.client.get(
            "/polls/videos/recommendations/?metadata[duration:lt:int]=120"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["entity"]["metadata"]["duration"], 10)

        response = self.client.get(
            "/polls/videos/recommendations/?metadata[duration:lte:int]=120"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data["results"]
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["entity"]["metadata"]["duration"], 120)
        self.assertEqual(results[1]["entity"]["metadata"]["duration"], 10)

    def test_anon_can_list_videos_filtered_by_duration_gt(self):
        response = self.client.get(
            "/polls/videos/recommendations/?metadata[duration:gt:int]=120"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["entity"]["metadata"]["duration"], 240)

        response = self.client.get(
            "/polls/videos/recommendations/?metadata[duration:gte:int]=120"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data["results"]
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["entity"]["metadata"]["duration"], 240)
        self.assertEqual(results[1]["entity"]["metadata"]["duration"], 120)

    def test_anon_can_list_videos_filtered_by_duration_illegal(self):
        """
        The special string "__" must be forbidden in any metadata filter
        field.
        """
        response = self.client.get(
            "/polls/videos/recommendations/?metadata[duration__lte::int]=10"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_anon_can_list_videos_duration_reject_empty_value(self):
        response = self.client.get(
            "/polls/videos/recommendations/?metadata[duration:lte:int]="
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_can_list_reco_with_score_mode(self):
        response = self.client.get(
            "/polls/videos/recommendations/?score_mode=all_equal&weights[reliability]=10&weights[importance]=10&weights[largely_recommended]=0"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data["results"]
        self.assertEqual(len(results), 3)

        self.assertEqual(results[0]["entity"]["uid"], self.video_3.uid)
        self.assertEqual(results[0]["recommendation_metadata"]["total_score"], 5.0)
        self.assertEqual(results[1]["entity"]["uid"], self.video_4.uid)
        self.assertEqual(results[1]["recommendation_metadata"]["total_score"], 4.0)
        self.assertEqual(results[2]["entity"]["uid"], self.video_2.uid)
        self.assertEqual(results[2]["recommendation_metadata"]["total_score"], -2.0)

    def test_can_list_reco_with_mehestan_default_weights(self):
        response = self.client.get(
            "/polls/videos/recommendations/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["results"]
        self.assertEqual(len(results), 3)

    def test_users_can_search_video_by_tags(self):
        """
        Users can perform a full text search in the videos' tags.
        """
        self.video_1.metadata["tags"] = ["tag 1", "tag 2", "tag 3"]
        self.video_1.save()
        self.video_2.metadata["tags"] = ["tag 4"]
        self.video_2.save()

        response = self.client.get("/polls/videos/recommendations/?search=tag")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["entity"]["uid"], self.video_2.uid)

        self.video_3.metadata["tags"] = ["tag 5"]
        self.video_3.save()

        cache.clear()
        response = self.client.get("/polls/videos/recommendations/?search=tag")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)
        self.assertEqual(response.data["results"][0]["entity"]["uid"], self.video_3.uid)
        self.assertEqual(response.data["results"][1]["entity"]["uid"], self.video_2.uid)


class PollsRecommendationsFilterRatedEntitiesTestCase(TestCase):
    """
    TestCase of the PollsRecommendationsView API.
    """

    def setUp(self):
        self.client = APIClient()
        self.videos = [
            VideoFactory(tournesol_score=92, n_contributors=3) for _ in range(4)
        ]
        self.video_1, self.video_2, self.video_3, self.video_4 = self.videos
        self.criteria_scores = [
            VideoCriteriaScoreFactory(entity=video, score=2) for video in self.videos
        ]
        self.user_no_comparisons = UserFactory()
        self.user_with_ratings = UserFactory()
        ComparisonFactory(user=self.user_with_ratings, entity_1=self.video_1, entity_2=self.video_3)
        # User has created a Rating, but has not compared the video
        ContributorRatingFactory(user=self.user_with_ratings, entity=self.video_4)

    def test_exclude_option_ignored_for_anonymous(self):
        response_exclude_false = self.client.get("/polls/videos/recommendations/?exclude_compared_entities=false")
        results_exclude_false = response_exclude_false.data["results"]
        response_exclude_true = self.client.get("/polls/videos/recommendations/?exclude_compared_entities=true")
        results_exclude_true = response_exclude_true.data["results"]
        self.assertEqual(len(results_exclude_false), 4)
        self.assertListEqual(results_exclude_false, results_exclude_true)

    def test_user_no_comparison_has_no_entity_excluded(self):
        self.client.force_authenticate(user=self.user_no_comparisons)
        response = self.client.get("/polls/videos/recommendations/?exclude_compared_entities=true")
        results = response.data["results"]
        self.assertEqual(len(results), 4)

    def test_user_with_ratings_has_no_entity_excluded_by_default(self):
        self.client.force_authenticate(user=self.user_with_ratings)
        response = self.client.get("/polls/videos/recommendations/")
        results = response.data["results"]
        self.assertEqual(len(results), 4)

    def test_user_with_ratings_can_list_all_entities(self):
        self.client.force_authenticate(user=self.user_with_ratings)
        response = self.client.get("/polls/videos/recommendations/?exclude_compared_entities=false")
        results = response.data["results"]
        self.assertEqual(len(results), 4)

    def test_user_with_ratings_can_exclude_entities(self):
        self.client.force_authenticate(user=self.user_with_ratings)
        response = self.client.get("/polls/videos/recommendations/?exclude_compared_entities=true")
        results = response.data["results"]
        self.assertSetEqual(set(e["entity"]["uid"] for e in results), {self.video_2.uid, self.video_4.uid})

    def test_response_is_not_cached_when_exclude_is_true(self):
        response = self.client.get("/polls/videos/recommendations/?exclude_compared_entities=true")
        self.client.force_authenticate(user=self.user_with_ratings)
        response = self.client.get("/polls/videos/recommendations/?exclude_compared_entities=true", HTTP_AUTHORIZATION="abc")
        results = response.data["results"]
        self.assertSetEqual(set(e["entity"]["uid"] for e in results), {self.video_2.uid, self.video_4.uid})

    def test_response_is_not_cached_when_exclude_is_true_for_two_users(self):
        self.client.force_authenticate(user=self.user_with_ratings)
        response = self.client.get("/polls/videos/recommendations/?exclude_compared_entities=true", HTTP_AUTHORIZATION="abc")
        self.client.force_authenticate(user=self.user_no_comparisons)
        response = self.client.get("/polls/videos/recommendations/?exclude_compared_entities=true", HTTP_AUTHORIZATION="def")
        results = response.data["results"]
        self.assertEqual(len(results), 4)

    def test_response_is_cached_when_exclude_is_false(self):
        self.client.force_authenticate(user=self.user_no_comparisons)
        response = self.client.get("/polls/videos/recommendations/?exclude_compared_entities=false", HTTP_AUTHORIZATION="abc")
        new_video = VideoFactory(tournesol_score=2.2, n_contributors=3)
        VideoCriteriaScoreFactory(entity=new_video, score=2)
        self.client.force_authenticate(user=self.user_no_comparisons)
        response = self.client.get("/polls/videos/recommendations/?exclude_compared_entities=false", HTTP_AUTHORIZATION="def")
        results = response.data["results"]
        self.assertEqual(len(results), 4)

    def test_response_anonymous_writes_to_cache_when_exclude_is_false(self):
        response = self.client.get("/polls/videos/recommendations/?exclude_compared_entities=false")
        new_video = VideoFactory(tournesol_score=2.2, n_contributors=3)
        VideoCriteriaScoreFactory(entity=new_video, score=2)
        self.client.force_authenticate(user=self.user_no_comparisons)
        response = self.client.get("/polls/videos/recommendations/?exclude_compared_entities=false", HTTP_AUTHORIZATION="def")
        results = response.data["results"]
        self.assertEqual(len(results), 4)

    def test_response_anonymous_reads_from_cache_when_exclude_is_false(self):
        self.client.force_authenticate(user=self.user_no_comparisons)
        response = self.client.get("/polls/videos/recommendations/?exclude_compared_entities=false", HTTP_AUTHORIZATION="def")
        new_video = VideoFactory(tournesol_score=2.2, n_contributors=3)
        VideoCriteriaScoreFactory(entity=new_video, score=2)
        self.client.force_authenticate(user=None)
        response = self.client.get("/polls/videos/recommendations/?exclude_compared_entities=false")
        results = response.data["results"]
        self.assertEqual(len(results), 4)

    def test_user_rated_everything_sees_empty_results(self):
        self.client.force_authenticate(user=self.user_with_ratings)
        ComparisonFactory(user=self.user_with_ratings, entity_1=self.video_2, entity_2=self.video_4)
        response = self.client.get("/polls/videos/recommendations/?exclude_compared_entities=true")
        results = response.data["results"]
        self.assertEqual(len(results), 0)

    def test_exluced_compared_entities_with_duplicated_entities_in_comparisons(self):
        self.client.force_authenticate(user=self.user_with_ratings)
        ComparisonFactory(user=self.user_with_ratings, entity_1=self.video_1, entity_2=self.video_2)
        ComparisonFactory(user=self.user_with_ratings, entity_1=self.video_2, entity_2=self.video_3)
        response = self.client.get("/polls/videos/recommendations/?exclude_compared_entities=true")
        results = response.data["results"]
        self.assertEqual(len(results), 1)
        self.assertSetEqual(set(e["entity"]["uid"] for e in results), {self.video_4.uid})


class PollsEntityTestCase(TestCase):
    """
    TestCase of the PollsEntityView API.
    """

    # users available in all tests
    _user = "username"

    # videos available in all tests
    _uid_01 = "yt:video_id_01"

    _non_existing_uid = "yt:_non_existing"
    _non_existing_poll = "_non_existing"

    def setUp(self):
        self.client = APIClient()

        self.video_1 = VideoFactory(
            uid="yt:video_id_01",
            tournesol_score=-2,
            n_contributors=4,
            n_comparisons=8
        )
        self.user = UserFactory(username=self._user)

    def test_auth_can_read(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f"/polls/videos/entities/{self.video_1.uid}")

        data = response.data
        self.assertEqual(response.status_code, 200)

        self.assertEqual(data["collective_rating"]["tournesol_score"], -2)
        self.assertEqual(data["collective_rating"]["n_comparisons"], 8)
        self.assertEqual(data["collective_rating"]["n_contributors"], 4)
        self.assertEqual(data["collective_rating"]["unsafe"], {
            "status": True,
            "reasons": ["insufficient_tournesol_score"],
        })
        self.assertIn("total_score", data["recommendation_metadata"])
        self.assertIn("criteria_scores", data["collective_rating"])

    def test_anon_can_read(self):
        response = self.client.get(f"/polls/videos/entities/{self.video_1.uid}")

        data = response.data
        self.assertEqual(response.status_code, 200)

        self.assertEqual(data["collective_rating"]["tournesol_score"], -2)
        self.assertEqual(data["collective_rating"]["n_comparisons"], 8)
        self.assertEqual(data["collective_rating"]["n_contributors"], 4)
        self.assertEqual(data["collective_rating"]["unsafe"], {
            "status": True,
            "reasons": ["insufficient_tournesol_score"],
        })
        self.assertIn("total_score", data["recommendation_metadata"])
        self.assertIn("criteria_scores", data["collective_rating"])


    def test_users_can_read_entity_without_score(self):
        self.video_1.all_poll_ratings.all().delete()

        response = self.client.get(f"/polls/videos/entities/{self.video_1.uid}")
        data = response.data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data["entity"]["uid"], self.video_1.uid)
        self.assertEqual(data["collective_rating"], None)

    def test_users_read_404_if_uid_doesnt_exist(self):
        # anonymous user
        response = self.client.get(f"/polls/videos/entities/{self._non_existing_uid}")
        self.assertEqual(response.status_code, 404)

        # authenticated user
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f"/polls/videos/entities/{self._non_existing_uid}")
        self.assertEqual(response.status_code, 404)

    def test_users_read_404_if_poll_doesnt_exist(self):
        # anonymous user
        response = self.client.get(
            f"/polls/{self._non_existing_poll}/entities/{self.video_1.uid}"
        )
        self.assertEqual(response.status_code, 404)

        # authenticated user
        self.client.force_authenticate(user=self.user)
        response = self.client.get(
            f"/polls/{self._non_existing_poll}/entities/{self.video_1.uid}"
        )
        self.assertEqual(response.status_code, 404)


class PollsCriteriaScoreDistributionTestCase(TestCase):
    """
    TestCase of the PollsCriteriaScoreDistributionView API.
    """

    def setUp(self):
        self.client = APIClient()
        self.poll_videos = Poll.default_poll()

        user1 = User.objects.create_user(username="user1", email="test1@example.test")
        user2 = User.objects.create_user(username="user2", email="test2@example.test")

        self.entity_public = EntityFactory()
        self.entity_private = EntityFactory()

        self.contributor_ratings_1 = ContributorRatingFactory(
            user=user1, entity=self.entity_public, is_public=True
        )
        self.contributor_ratings_2 = ContributorRatingFactory(
            user=user2, entity=self.entity_public, is_public=True
        )

        self.contributor_ratings_private_1 = ContributorRatingFactory(
            user=user1, entity=self.entity_private, is_public=False
        )
        self.contributor_ratings_private_2 = ContributorRatingFactory(
            user=user2, entity=self.entity_private, is_public=False
        )

    def test_basic_api_call_is_successfull(self):
        response = self.client.get(
            f"/polls/videos/entities/{self.entity_public.uid}/criteria_scores_distributions"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_basic_call_missing_entity(self):
        response = self.client.get(
            "/polls/videos/entities/XYZ/criteria_scores_distributions"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_one_criteria_score_should_have_base_distribution(self):
        ContributorRatingCriteriaScoreFactory(
            contributor_rating=self.contributor_ratings_1,
            criteria="reliability",
            score=0.1,
        )
        response = self.client.get(
            f"/polls/videos/entities/{self.entity_public.uid}/criteria_scores_distributions"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["criteria_scores_distributions"]), 1)
        self.assertEqual(
            response.data["criteria_scores_distributions"][0]["criteria"], "reliability"
        )
        # The eleventh position are values between (0, 0.1) because
        # we use a 20 bins between (-1, 1)
        self.assertEqual(
            response.data["criteria_scores_distributions"][0]["distribution"][10], 1
        )

    def test_two_criteria_score_should_have_right_distribution(self):
        ContributorRatingCriteriaScoreFactory(
            contributor_rating=self.contributor_ratings_1,
            criteria="reliability",
            score=2,
        )
        ContributorRatingCriteriaScoreFactory(
            contributor_rating=self.contributor_ratings_2,
            criteria="reliability",
            score=95,
        )

        response = self.client.get(
            f"/polls/videos/entities/{self.entity_public.uid}/criteria_scores_distributions"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["criteria_scores_distributions"]), 1)
        self.assertEqual(
            response.data["criteria_scores_distributions"][0]["criteria"], "reliability"
        )
        # The eleventh position are values between (0, 10) because
        # we use a 20 bins between (-100, 100)
        self.assertEqual(
            response.data["criteria_scores_distributions"][0]["distribution"][10], 1
        )
        # The 20th position are all values above 90 because we use a 20 bins between (-100, 100)
        self.assertEqual(
            response.data["criteria_scores_distributions"][0]["distribution"][19], 1
        )
        # Distribution is always in a range [-100,100]
        self.assertEqual(
            min(response.data["criteria_scores_distributions"][0]["bins"]), -100
        )
        self.assertEqual(
            max(response.data["criteria_scores_distributions"][0]["bins"]), 100
        )

    def test_no_private_criteria_ratings_should_be_in_distribution(self):
        ContributorRatingCriteriaScoreFactory(
            contributor_rating=self.contributor_ratings_private_1,
            criteria="better_habits",
            score=2,
        )
        ContributorRatingCriteriaScoreFactory(
            contributor_rating=self.contributor_ratings_private_2,
            criteria="reliability",
            score=6,
        )

        response = self.client.get(
            f"/polls/videos/entities/{self.entity_private.uid}/criteria_scores_distributions"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["criteria_scores_distributions"]), 0)

    def test_all_criteria_ratings_should_be_in_distribution(self):
        ContributorRatingCriteriaScoreFactory(
            contributor_rating=self.contributor_ratings_1,
            criteria="better_habits",
            score=2,
        )
        ContributorRatingCriteriaScoreFactory(
            contributor_rating=self.contributor_ratings_2,
            criteria="reliability",
            score=6,
        )

        response = self.client.get(
            f"/polls/videos/entities/{self.entity_public.uid}/criteria_scores_distributions"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["criteria_scores_distributions"]), 2)

    def test_value_in_minus_1_plus_1_should_have_default_bins(self):
        ContributorRatingCriteriaScoreFactory(
            contributor_rating=self.contributor_ratings_1,
            criteria="better_habits",
            score=0.6,
        )
        ContributorRatingCriteriaScoreFactory(
            contributor_rating=self.contributor_ratings_2,
            criteria="better_habits",
            score=-0.6,
        )

        response = self.client.get(
            f"/polls/videos/entities/{self.entity_public.uid}/criteria_scores_distributions"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["criteria_scores_distributions"]), 1)
        self.assertEqual(
            min(response.data["criteria_scores_distributions"][0]["bins"]), -100
        )
        self.assertEqual(
            max(response.data["criteria_scores_distributions"][0]["bins"]), 100
        )

class PollRecommendationsWithLowSumTrustScoresTestCase(TestCase):
    """
    TestCase of the PollsRecommendationsView API related to the exclusion of
    entities with not enough sum of trust scores.
    """

    def setUp(self):
        self.client = APIClient()
        epr1 = EntityPollRatingFactory(sum_trust_scores=1, tournesol_score=42)
        epr2 =  EntityPollRatingFactory(sum_trust_scores=3, tournesol_score=42)
        self.video_1 = epr1.entity
        self.video_2 = epr2.entity
        VideoCriteriaScoreFactory(entity=self.video_1, score=42)
        VideoCriteriaScoreFactory(entity=self.video_2, score=42)

    def test_low_sum_trust_scores_excluded_from_recommendations(self):
        response = self.client.get("/polls/videos/recommendations/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data["results"]
        self.assertEqual(len(results), 1)

        self.assertEqual(
            results[0]["entity"]["uid"],
            self.video_2.uid,
        )
        self.assertEqual(
            results[0]["collective_rating"]["unsafe"],
            {
                "status": False,
                "reasons": []
            }
        )
