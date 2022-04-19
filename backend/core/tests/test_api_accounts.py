from unittest.mock import patch

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
    _existing_email_alt = "EXISTING@example.org"

    _non_existing_username = "non-existing"
    _non_existing_email = "non-existing@example.org"

    def setUp(self):
        self.client = APIClient()
        self.existing_user: User = UserFactory(
            username=self._existing_username, email=self._existing_email
        )

    def test_register_account_with_already_used_email(self) -> None:
        """
        An anonymous user can't register with a variant of an email address
        already in use.
        """
        n_users = User.objects.all().count()

        # a user cannot use an email address already in use
        invalid_payload = {
            "username": self._non_existing_username,
            "email": self._existing_email,
            "password": "very_uncommon_password",
            "password_confirm": "very_uncommon_password",
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
            "password": "very_uncommon_password",
            "password_confirm": "very_uncommon_password",
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
            "password": "very_uncommon_password",
            "password_confirm": "very_uncommon_password",
        }
        response = self.client.post(
            "/accounts/register/",
            valid_payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.all().count(), n_users + 1)

    def test_register_account_with_symbol_plus(self) -> None:
        """
        An anonymous user can't register with an email containing one or several
        plus symbols, if a similar address without plus is already in use.
        """
        n_users = User.objects.all().count()

        for email in [
            "existing+@example.org",
            "existing+@EXAMPLE.org",
            "existing+tournesol@example.org",
            "EXISTING+tournesol@example.org",
            "existing+TOURNESOL@example.org",
            "existing+foo+bar@example.org",
        ]:

            invalid_payload = {
                "username": self._non_existing_username,
                "email": email,
                "password": "very_uncommon_password",
                "password_confirm": "very_uncommon_password",
            }
            response = self.client.post(
                "/accounts/register/",
                invalid_payload,
                format="json",
            )
            self.assertEqual(
                response.status_code,
                status.HTTP_400_BAD_REQUEST,
                f"{email} was unexpectedly authorized even if {self._existing_email} was in DB",
            )
            self.assertIn("email", response.data)
            self.assertEqual(User.objects.all().count(), n_users)

    def test_register_account_with_symbol_plus_reverse(self) -> None:
        """
        An anonymous user can't register with an email containing no plus
        symbol, if a similar address with plus is already in use.
        """
        used_email = "already_USED+tournesol@example.org"
        used_email_noplus = "already_used@example.org"
        UserFactory(email=used_email)

        n_users = User.objects.all().count()

        invalid_payload = {
            "username": self._non_existing_username,
            "email": used_email_noplus,
            "password": "very_uncommon_password",
            "password_confirm": "very_uncommon_password",
        }
        response = self.client.post(
            "/accounts/register/",
            invalid_payload,
            format="json",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            f"{used_email_noplus} was unexpectedly authorized even if {used_email} was in DB",
        )
        self.assertIn("email", response.data)
        self.assertEqual(User.objects.all().count(), n_users)

    def test_register_account_with_symbol_plus_different(self) -> None:
        """
        An anonymous user can't register with an email containing one or several
        plus symbols, if a similar address with plus is already in use.
        """
        already_used = "already_USED+tournesol@example.org"
        UserFactory(email=already_used)
        n_users = User.objects.all().count()

        for email in [
            "already_used+@example.org",
            "already_used+@EXAMPLE.org",
            "ALREADY_USED+tournesol@example.org",
            "already_used+TOURNESOL@example.org",
            "already_used+different@example.org",
            "already_used+foo+bar@example.org",
        ]:

            invalid_payload = {
                "username": self._non_existing_username,
                "email": email,
                "password": "very_uncommon_password",
                "password_confirm": "very_uncommon_password",
            }
            response = self.client.post(
                "/accounts/register/",
                invalid_payload,
                format="json",
            )
            self.assertEqual(
                response.status_code,
                status.HTTP_400_BAD_REQUEST,
                f"{email} was unexpectedly authorized even if {already_used} was in DB",
            )
            self.assertIn("email", response.data)
            self.assertEqual(User.objects.all().count(), n_users)

    def test_register_email_with_already_used_email(self) -> None:
        """
        An authenticated user can't update its email with a variant already
        in use.
        """
        used_email = "already_used@example.org"
        used_email_alt = "already_USED@example.org"
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

    def test_register_email_with_symbol_plus(self) -> None:
        used_email = "already_USED@example.org"
        UserFactory(email=used_email)

        self.client.force_authenticate(user=self.existing_user)

        for email in [
            "already_used+@example.org",
            "already_used+@EXAMPLE.org",
            "ALREADY_USED+tournesol@example.org",
            "already_used+TOURNESOL@example.org",
            "already_used+foo+bar@example.org",
        ]:
            response = self.client.post(
                "/accounts/register-email/",
                {"email": email},
                format="json",
            )
            self.assertEqual(
                response.status_code,
                status.HTTP_400_BAD_REQUEST,
                f"{email} was unexpectedly authorized even if {self._existing_email} was in DB",
            )
            self.assertIn("email", response.data)

    def test_register_email_with_symbol_plus_reverse(self) -> None:
        used_email = "already_USED+tournesol@example.org"
        used_email_noplus = "already_used@example.org"
        UserFactory(email=used_email)

        self.client.force_authenticate(user=self.existing_user)

        response = self.client.post(
            "/accounts/register-email/",
            {"email": used_email_noplus},
            format="json",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            f"{used_email_noplus} was unexpectedly authorized even if {used_email} was in DB",
        )
        self.assertIn("email", response.data)


class AccountsResetPasswordTestCase(TestCase):
    """
    TestCase of the /accounts/reset-password/ API.

    Even if this API is provided by a third-party package, its default
    behaviour has been customized, and thus needs to be tested.
    """

    @patch("rest_registration.utils.signers.DataSigner.verify", new=lambda x: True)
    def test_reset_password_force_user_activation(self):
        client = APIClient()
        user = UserFactory(is_active=False)

        resp = client.post(
            "/accounts/reset-password/",
            data={
                "user_id": user.id,
                "password": "very_uncommon_pwd",
                "timestamp": 123,
                "signature": "abc",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 200, resp.content)

        user.refresh_from_db()
        self.assertTrue(user.is_active)
