from django.test import TestCase
from rest_framework.test import APIClient


class PollsApi(TestCase):
    def test_anonymous_can_read(self):
        """An anonymous user can read a poll with its translated criteria."""
        client = APIClient(HTTP_ACCEPT_LANGUAGE="fr")
        response = client.get("/polls/videos/")
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data["name"], "videos")
        self.assertEqual(len(response_data["criterias"]), 10)
        self.assertEqual(response_data["criterias"][0], {
            "name": "largely_recommended",
            "label": "Devrait être largement recommandé",
            "optional": False,
        })
