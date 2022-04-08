from unittest.mock import patch

from django.test import TestCase
from rest_framework.test import APIClient

from core.tests.factories.user import UserFactory


class TestPasswordReset(TestCase):

    @patch("rest_registration.utils.verification.verify_signer_or_bad_request", new= lambda x:True)
    def test_reset_password_force_user_activation(self):
        client = APIClient()
        user = UserFactory(is_active=False)

        resp = client.post("/accounts/reset-password/", data={
            "user_id": user.id,
            "password": "new_password",
            "timestamp": 123,
            "signature": "abc",
        }, format="json")
        self.assertEqual(resp.status_code, 200, resp.content)

        user.refresh_from_db()
        self.assertTrue(user.is_active)
