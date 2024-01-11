from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from tournesol.models import Poll
from tournesol.tests.factories.entity import VideoFactory


class RandomRecommendationTestCase(TestCase):
    """
    TestCase of the RandomRecommendationList view.
    """

    def setUp(self):
        self.client = APIClient()
        self.poll = Poll.default_poll()
        self.url_path = "/polls/videos/recommendations/random/"

        self.video_1 = VideoFactory(
            metadata__name="unsafe",
            metadata__publication_date="2021-01-01",
            metadata__uploader="_test_uploader_1",
            metadata__language="es",
            tournesol_score=-1,
            make_safe_for_poll=False,
        )
        self.video_2 = VideoFactory(
            metadata__name="safe__22",
            metadata__publication_date="2021-01-02",
            metadata__uploader="_test_uploader_2",
            metadata__language="fr",
            metadata__duration=10,
            tournesol_score=22,
            make_safe_for_poll=False,
        )
        self.video_3 = VideoFactory(
            metadata__name="safe__33",
            metadata__publication_date="2021-01-03",
            metadata__uploader="_test_uploader_2",
            metadata__language="pt",
            metadata__duration=120,
            tournesol_score=33,
            make_safe_for_poll=False,
        )
        self.video_4 = VideoFactory(
            metadata__name="safe__44",
            metadata__publication_date="2021-01-04",
            metadata__uploader="_test_uploader_3",
            metadata__language="it",
            metadata__duration=240,
            tournesol_score=44,
            make_safe_for_poll=False,
        )

    def test_anon_can_list(self):
        resp = self.client.get(self.url_path)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        results = resp.data["results"]
        self.assertEqual(len(results), 3)

        uids = [res["entity"]["uid"] for res in results]

        self.assertNotIn(self.video_1.uid, uids)
        self.assertIn(self.video_2.uid, uids)
        self.assertIn(self.video_3.uid, uids)
        self.assertIn(self.video_4.uid, uids)

        for result in results:
            self.assertEqual(result["entity_contexts"], [])

    def test_list_is_poll_specific(self):
        resp = self.client.get(f"{self.url_path}?random=1")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data["results"]), 3)

        other_poll = Poll.objects.create(name="other")
        video_5 = VideoFactory.create(make_safe_for_poll=other_poll)

        resp = self.client.get(f"{self.url_path}?random=2")
        results = resp.data["results"]
        uids = [res["entity"]["uid"] for res in results]

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(results), 3)
        self.assertNotIn(video_5.uid, uids)

    def test_anon_can_list_with_limit(self):
        """
        An anonymous user can limit the size of the results by using the
        `limit` query parameter.
        """
        resp = self.client.get(f"{self.url_path}?limit=1")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data["results"]), 1)

    def test_anon_can_list_videos_filtered_by_metadata(self):
        """
        Anonymous users can filter the recommended videos using a single
        value filter.
        """
        resp = self.client.get(f"{self.url_path}?metadata[uploader]=_test_uploader_3")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data["results"]), 1)
        self.assertEqual(resp.data["results"][0]["entity"]["uid"], self.video_4.uid)

        # filtering by an unknown upload must return an empty list
        resp = self.client.get(f"{self.url_path}?metadata[uploader]=unknown_uploader")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["count"], 0)
        self.assertEqual(resp.data["results"], [])

    def test_anon_can_list_videos_filtered_by_pub_date(self):
        """
        Anonymous users can filter the recommended videos using a single
        value filter.
        """
        resp = self.client.get(f"{self.url_path}?date_lte=2021-01-02")
        results = resp.data["results"]
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["entity"]["uid"], self.video_2.uid)

        resp = self.client.get(f"{self.url_path}?date_lte=2021-01-03")
        results = resp.data["results"]
        uids = [res["entity"]["uid"] for res in results]

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(results), 2)
        self.assertIn(self.video_2.uid, uids)
        self.assertIn(self.video_3.uid, uids)

        resp = self.client.get(f"{self.url_path}?date_gte=2021-01-01")
        results = resp.data["results"]
        uids = [res["entity"]["uid"] for res in results]

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(results), 3)
        self.assertIn(self.video_2.uid, uids)
        self.assertIn(self.video_3.uid, uids)
        self.assertIn(self.video_4.uid, uids)
