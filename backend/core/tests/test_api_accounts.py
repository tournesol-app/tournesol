from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models.user import User
from core.tests.factories.user import UserFactory


class AccountsRegisterTestCase(TestCase):
    """
    TestCase of the /accounts/register/ API.

    Even if this API is provided by a third-party package, its default
    behaviour has been customized, and thus needs to be tested.
    """
    _existing_username = "existing"
    _existing_email = "existing@example.org"
    _existing_email_alt = "Existing@example.org"

    _non_existing_username = "non-existing"
    _non_existing_email = "non-existing@example.org"

    def setUp(self):
        self.client = APIClient()
        self.existing_user: User = UserFactory(
            username=self._existing_username, email=self._existing_email
        )

    def test_register_with_already_used_email(self) -> None:
        """
        An anonymous user can't register with a variant of an email address
        already in use.
        """
        n_users = User.objects.all().count()

        # a user cannot use an email address already in use
        invalid_payload = {
            "username": self._non_existing_username,
            "email": self._existing_email,
            "password": "password",
            "password_confirm": "password",
        }
        response = self.client.post(
            "/accounts/register/",
            invalid_payload,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
        self.assertEqual(User.objects.all().count(), n_users)

        # a user cannot use a lower/upper variant of an email address already
        # in use
        invalid_payload = {
            "username": self._non_existing_username,
            "email": self._existing_email_alt,
            "password": "password",
            "password_confirm": "password",
        }
        response = self.client.post(
            "/accounts/register/",
            invalid_payload,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
        self.assertEqual(User.objects.all().count(), n_users)

        # using a new email address is obviously valid
        valid_payload = {
            "username": self._non_existing_username,
            "email": self._non_existing_email,
            "password": "uncommon_password",
            "password_confirm": "uncommon_password",
        }
        response = self.client.post(
            "/accounts/register/",
            valid_payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.all().count(), n_users + 1)

    def test_register_email_with_already_used_email(self) -> None:
        """
        An authenticated user can't register with a variant of an email
        address already in use.
        """
        used_email = "also_used@example.org"
        used_email_alt = "also_USED@example.org"

        UserFactory(email=used_email)
        self.client.force_authenticate(user=self.existing_user)

        # a user cannot use an email address already in use
        response = self.client.post(
            "/accounts/register-email/",
            {"email": used_email},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

        # a user cannot use a lower/upper variant of an email address already
        # in use
        response = self.client.post(
            "/accounts/register-email/",
            {"email": used_email_alt},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

        # using a new email address is obviously valid
        response = self.client.post(
            "/accounts/register-email/",
            {"email": self._non_existing_email},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
