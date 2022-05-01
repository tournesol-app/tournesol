from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from tournesol.models import Poll

from .factories.entity import VideoCriteriaScoreFactory, VideoFactory


class PollsApi(TestCase):
    def test_anonymous_can_read(self):
        """An anonymous user can read a poll with its translated criteria."""
        client = APIClient(HTTP_ACCEPT_LANGUAGE="fr")
        response = client.get("/polls/videos/")
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data["name"], "videos")
        self.assertEqual(len(response_data["criterias"]), 10)
        self.assertEqual(
            response_data["criterias"][0],
            {
                "name": "largely_recommended",
                "label": "Devrait être largement recommandé",
                "optional": False,
            },
        )


class PollsRecommendationsApi(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.video_1 = VideoFactory(
            metadata__publication_date="2021-01-01",
            metadata__uploader="_test_uploader_1",
            metadata__language="es",
            tournesol_score=1.1,
            rating_n_contributors=2,
        )
        self.video_2 = VideoFactory(
            metadata__publication_date="2021-01-02",
            metadata__uploader="_test_uploader_2",
            metadata__language="fr",
            tournesol_score=2.2,
            rating_n_contributors=3,
        )
        self.video_3 = VideoFactory(
            metadata__publication_date="2021-01-03",
            metadata__uploader="_test_uploader_2",
            metadata__language="pt",
            tournesol_score=3.3,
            rating_n_contributors=4,
        )
        self.video_4 = VideoFactory(
            metadata__publication_date="2021-01-04",
            metadata__uploader="_test_uploader_3",
            metadata__language="it",
            tournesol_score=4.4,
            rating_n_contributors=5,
        )

        VideoCriteriaScoreFactory(entity=self.video_1, criteria="reliability", score=-0.1)
        VideoCriteriaScoreFactory(entity=self.video_2, criteria="reliability", score=0.2)
        VideoCriteriaScoreFactory(entity=self.video_3, criteria="importance", score=0.3)
        VideoCriteriaScoreFactory(entity=self.video_4, criteria="importance", score=0.4)

    def test_anonymous_can_list_recommendations(self):
        response = self.client.get("/polls/videos/recommendations/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data["results"]
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]["tournesol_score"], 4.4)
        self.assertEqual(results[1]["tournesol_score"], 3.3)
        self.assertEqual(results[2]["tournesol_score"], 2.2)

        self.assertEqual(results[0]["type"], "video")

    def test_ignore_score_attached_to_another_poll(self):
        other_poll = Poll.objects.create(name="other")
        video_5 = VideoFactory(
            metadata__publication_date="2021-01-05",
            rating_n_contributors=6,
        )
        VideoCriteriaScoreFactory(
            poll=other_poll, entity=video_5, criteria="importance", score=0.5
        )
        response = self.client.get("/polls/videos/recommendations/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 3)

    def test_anonymous_can_list_unsafe_recommendations(self):
        response = self.client.get("/polls/videos/recommendations/?unsafe=true")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 4)

    def test_anonymous_can_list_with_offset(self):
        """
        An anonymous user can list a subset of videos by using the `offset`
        query parameter.
        """
        response = self.client.get("/polls/videos/recommendations/?offset=2")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_list_videos_with_criteria_weights(self):
        # Default weights: all criterias contribute equally
        resp = self.client.get("/polls/videos/recommendations/")
        self.assertEqual(
            [r["uid"] for r in resp.data["results"]],
            [self.video_4.uid, self.video_3.uid, self.video_2.uid],
        )

        # Disable reliability
        resp = self.client.get("/polls/videos/recommendations/?weights[reliability]=0")
        self.assertEqual(
            [r["uid"] for r in resp.data["results"]],
            [self.video_4.uid, self.video_3.uid],
        )

        # Disable both reliability and importance
        resp = self.client.get(
            "/polls/videos/recommendations/?weights[reliability]=0&weights[importance]=0"
        )
        self.assertEqual([r["uid"] for r in resp.data["results"]], [])

        # More weight to reliability should change the order
        resp = self.client.get(
            "/polls/videos/recommendations/?weights[reliability]=100&weights[importance]=10"
        )
        self.assertEqual(
            [r["uid"] for r in resp.data["results"]],
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
            [video["uid"] for video in resp.data["results"]],
            [self.video_3.uid, self.video_2.uid],
        )

        resp = self.client.get(
            "/polls/videos/recommendations/?metadata[uploader]=_test_uploader_3"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["results"][0]["uid"], self.video_4.uid)

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
        self.assertEqual(resp.data["results"][0]["uid"], self.video_2.uid)

        resp = self.client.get(
            "/polls/videos/recommendations/?metadata[language]=fr"
            "&metadata[language]=pt""&metadata[language]=it"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [video["uid"] for video in resp.data["results"]],
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
            [video["uid"] for video in resp.data["results"]],
            [self.video_3.uid, self.video_2.uid],
        )

        resp = self.client.get(
            "/polls/videos/recommendations/?metadata[uploader]=unknown_uploader"
            "&metadata[language]=fr&metadata[language]=pt&metadata[language]=it"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["count"], 0)
        self.assertEqual(resp.data["results"], [])
