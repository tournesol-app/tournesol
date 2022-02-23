from unittest.mock import ANY

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from tournesol.models import Poll

from .factories.video import VideoCriteriaScoreFactory, VideoFactory


class EntitiesApi(TestCase):
    def setUp(self):
        self.client = APIClient()
        poll2 = Poll.objects.create(name="poll2")
        self.video = VideoFactory()

        # Scores for default poll "videos"
        VideoCriteriaScoreFactory(entity=self.video)
        VideoCriteriaScoreFactory.create_batch(2)

        # Scores for "poll2"
        VideoCriteriaScoreFactory(entity=self.video, poll=poll2)
        VideoCriteriaScoreFactory.create_batch(1, poll=poll2)

    def test_anonymous_can_list(self):
        response = self.client.get("/entities/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 4)
        self.assertDictEqual(
            response.data["results"][0],
            {
                "uid": self.video.uid,
                "metadata": ANY,
                "type": "video",
                "polls": [
                    {
                        "name": "videos",
                        "criteria_scores": [
                            {"criteria": "better_habits", "score": ANY}
                        ],
                    },
                    {
                        "name": "poll2",
                        "criteria_scores": [
                            {"criteria": "better_habits", "score": ANY}
                        ],
                    },
                ],
            },
        )

    def test_anonymous_can_list_filter_by_type(self):
        response = self.client.get("/entities/?type=other")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)

        response = self.client.get("/entities/?type=video")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 4)

    def test_anonymous_can_list_filter_polls(self):
        response = self.client.get("/entities/?poll_name=videos")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 4)
        self.assertEqual(len(response.data["results"][0]["polls"]), 1)

    def test_anonymous_can_get_single_entity(self):
        response = self.client.get(f"/entities/{self.video.uid}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["uid"], self.video.uid)
