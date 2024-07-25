import csv
import io

from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient

from core.models import User
from tournesol.models import Poll
from tournesol.tests.factories.comparison import ComparisonFactory


@override_settings(SECRET_KEY="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
class ExportProofOfVote(TestCase):
    """
    Test case of the API /exports/polls/{poll_name}/proof_of_vote/
    """

    def setUp(self):
        self.client = APIClient()
        self.default_poll = Poll.default_poll()

    def test_anon_cant_get_proof_of_vote(self):
        """
        An anonymous user should not be able to download the proof of vote.
        """
        response = self.client.get(f"/exports/polls/{self.default_poll.name}/proof_of_vote/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_auth_non_staff_cant_get_proof_of_vote(self):
        """
        An authenticated non-administrator user should not be able to download the proof of vote.
        """
        user = User.objects.create_user(
            username="test_non_saff",
            email="test_non_saff@example.org",
            is_active=True,
            is_staff=False,
        )

        self.client.force_authenticate(user)
        response = self.client.get(f"/exports/polls/{self.default_poll.name}/proof_of_vote/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_auth_staff_can_get_proof_of_vote_empty(self):
        """
        An authenticated administrator user should be able to download an empty proof of vote.
        """
        user = User.objects.create_user(
            username="test_staff",
            email="test_staff@example.org",
            is_active=True,
            is_staff=True,
        )

        self.client.force_authenticate(user)
        response = self.client.get(f"/exports/polls/{self.default_poll.name}/proof_of_vote/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.headers["Content-Type"], "text/csv")

        csv_lines = [line for line in csv.reader(io.StringIO(response.content.decode()))]
        self.assertEqual(len(csv_lines), 1)
        self.assertEqual(
            csv_lines[0],
            [
                "user_id",
                "username",
                "email",
                "n_comparisons",
                "signature",
            ]
        )

    def test_auth_staff_can_get_proof_of_vote_non_empty(self):
        """
        An authenticated administrator user should be able to download the proof of vote.
        """
        user = User.objects.create_user(
            username="test_staff",
            email="test_staff@example.org",
            is_active=True,
            is_staff=True,
        )

        ComparisonFactory(poll=self.default_poll, user=user)
        self.client.force_authenticate(user)
        response = self.client.get(f"/exports/polls/{self.default_poll.name}/proof_of_vote/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.headers["Content-Type"], "text/csv")

        csv_lines = [line for line in csv.reader(io.StringIO(response.content.decode()))]
        self.assertEqual(len(csv_lines), 2)
        self.assertEqual(
            csv_lines[0],
            [
                "user_id",
                "username",
                "email",
                "n_comparisons",
                "signature",
            ]
        )
        self.assertEqual(
            csv_lines[1],
            [
                str(user.id),
                "test_staff",
                "test_staff@example.org",
                "1",
                self.default_poll.get_user_proof(user.id, "proof_of_vote"),
            ]
        )
