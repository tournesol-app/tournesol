from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from core.tests.factories.user import UserFactory

from .factories.comparison import ComparisonFactory
from .factories.poll import PollFactory


class PollsApi(TestCase):
    def setUp(self):
        self.poll = PollFactory()
        self.user1 = UserFactory(pk=42)
        self.user2 = UserFactory()
        ComparisonFactory(
            poll=self.poll,
            user=self.user1
        )

    def test_proof_of_vote_denied(self):
        """A user without comparison cannot retrieve a proof of vote"""
        client = APIClient()
        client.force_authenticate(self.user2)
        response = client.get(f"/users/me/proof_of_votes/{self.poll.name}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_proof_of_vote(self):
        """Retrieve a proof of vote """
        client = APIClient()
        client.force_authenticate(self.user1)
        response = client.get(f"/users/me/proof_of_votes/{self.poll.name}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["poll_name"], self.poll.name)
        self.assertTrue(response.data["signature"].startswith("00042:"))
