from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from core.tests.factories.user import UserFactory

from .factories.comparison import ComparisonFactory
from .factories.poll import PollFactory


class ProofViewTestCase(TestCase):
    def setUp(self):
        self.poll = PollFactory()
        self.client = APIClient()

        self.user_with_comparisons = UserFactory(pk=42)
        self.user_with_0_comparison = UserFactory(pk=84)
        ComparisonFactory(poll=self.poll, user=self.user_with_comparisons)

    def test_anon_401_cant_get_proof(self):
        """
        An anonymous user cannot get any proof.
        """
        response = self.client.get(f"/users/me/proof/{self.poll.name}/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(
            f"/users/me/proof/{self.poll.name}/", data={"keyword": ""}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(
            f"/users/me/proof/{self.poll.name}/",
            data={"keyword": "proof_of_vote"},
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_auth_200_can_get_default_proof(self):
        """
        An authenticated user can get a proof of activated account, even with
        no comparison.
        """
        self.client.force_authenticate(self.user_with_0_comparison)

        # No query parameter should be considered as a simple proof of account
        # request.
        response = self.client.get(f"/users/me/proof/{self.poll.name}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["signature"].startswith("00084:"))

        default_signature = response.data["signature"]

        # An empty query parameter should be considered as a simple proof of
        # account request.
        response = self.client.get(
            f"/users/me/proof/{self.poll.name}/", data={"keyword": ""}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["signature"], default_signature)

        # An empty query parameter should be considered as a simple proof of
        # account request.
        response = self.client.get(
            f"/users/me/proof/{self.poll.name}/", data={"keyword": "activated"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["signature"], default_signature)

    def test_auth_403_cant_get_proof_of_vote_without_comparison(self):
        """
        An authenticated user cannot get a proof of vote without comparison.
        """
        self.client.force_authenticate(self.user_with_0_comparison)
        response = self.client.get(
            f"/users/me/proof/{self.poll.name}/",
            data={"keyword": "proof_of_vote"},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_auth_200_can_get_proof_of_vote_with_comparisons(self):
        """
        An authenticated user with at least one comparison made can get a
        proof of vote.
        """
        self.client.force_authenticate(self.user_with_comparisons)
        response = self.client.get(
            f"/users/me/proof/{self.poll.name}/",
            data={"keyword": "proof_of_vote"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["poll_name"], self.poll.name)
        self.assertTrue(response.data["signature"].startswith("00042:"))
