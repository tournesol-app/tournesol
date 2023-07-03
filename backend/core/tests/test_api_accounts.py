from unittest.mock import patch

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from core.models.user import User
from core.tests.factories.user import UserFactory


class AccountRegisterMixin:
    """
    A mixin that factorizes behaviours common to all account
    registration test cases.
    """

    _existing_username = "existing"
    _existing_email = "existing@example.org"
    _existing_email_alt = "EXISTING@example.org"

    _non_existing_username = "non-existing"
    _non_existing_email = "non-existing@example.org"

    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.existing_user: User = UserFactory(
            username=self._existing_username, email=self._existing_email
        )


class AccountRegisterUser(AccountRegisterMixin, TestCase):
    """
    TestCase of the /accounts/register/ API related to the user settings.
    """
    def test_register_account(self):
        new_username = self._non_existing_username
        new_email = self._non_existing_email

        response = self.client.post(
            "/accounts/register/",
            data={
                "username": new_username,
                "email": new_email,
                "password": "very_uncommon_pwd",
                "password_confirm": "very_uncommon_pwd",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_data = response.json()
        self.assertEqual(response_data["username"], new_username)
        new_user = User.objects.get(username=new_username)
        self.assertEqual(new_user.email, new_email)

    def test_register_account_trust_score_read_only(self):
        new_username = self._non_existing_username
        new_email = self._non_existing_email
        response = self.client.post(
            "/accounts/register/",
            data={
                "username": new_username,
                "email": new_email,
                "password": "very_uncommon_pwd",
                "password_confirm": "very_uncommon_pwd",
                "trust_score": 0.99,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_data = response.json()
        self.assertEqual(response_data["trust_score"], None)
        new_user = User.objects.get(username=new_username)
        self.assertEqual(new_user.trust_score, None)

    def test_register_account_with_settings(self) -> None:
        """
        An anonymous user can define its settings during the registration.
        """

        user_settings = {
            "general": {
                "notifications_email__research": True,
                "notifications_email__new_features": True,
            }
        }
        # using a new email address is obviously valid
        valid_payload = {
            "username": self._non_existing_username,
            "email": self._non_existing_email,
            "password": "very_uncommon_pwd",
            "password_confirm": "very_uncommon_pwd",
            "settings": user_settings,
        }
        response = self.client.post(
            "/accounts/register/",
            valid_payload,
            format="json",
        )

        new_user = User.objects.get(username=self._non_existing_username)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertDictEqual(new_user.settings, user_settings)


class AccountsRegisterEmailTestCase(AccountRegisterMixin, TestCase):
    """
    TestCase of the /accounts/register/ API related to the emails.
    """

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
            "password": "very_uncommon_pwd",
            "password_confirm": "very_uncommon_pwd",
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
            "password": "very_uncommon_pwd",
            "password_confirm": "very_uncommon_pwd",
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
            "password": "very_uncommon_pwd",
            "password_confirm": "very_uncommon_pwd",
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
                "password": "very_uncommon_pwd",
                "password_confirm": "very_uncommon_pwd",
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
        symbol, if a similar address with a plus is already in use.
        """
        used_email = "already_USED+tournesol@example.org"
        used_email_noplus = "already_used@example.org"
        UserFactory(email=used_email)

        n_users = User.objects.all().count()

        invalid_payload = {
            "username": self._non_existing_username,
            "email": used_email_noplus,
            "password": "very_uncommon_pwd",
            "password_confirm": "very_uncommon_pwd",
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
        An anonymous user can't register with an email containing one or
        several plus symbols, if a similar address with a plus is already in
        use.
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
                "password": "very_uncommon_pwd",
                "password_confirm": "very_uncommon_pwd",
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
        """
        An authenticated user can't update its email with one containing one
        or several plus symbols, if a similar address without plus is already
        in use by another user.
        """
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
        """
        An authenticated user can't update its email with one containing no
        plus symbol, if a similar address with a plus is already in use by
        another user.
        """
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

    def test_register_email_with_symbol_plus_different(self) -> None:
        """
        An authenticated user can't update its email with one containing one
        or several plus symbols, if a similar address with plus is already in
        use by another user.
        """
        used_email = "already_USED+tournesol@example.org"
        UserFactory(email=used_email)

        self.client.force_authenticate(user=self.existing_user)

        for email in [
            "already_used+@example.org",
            "already_used+@EXAMPLE.org",
            "ALREADY_USED+tournesol@example.org",
            "already_used+TOURNESOL@example.org",
            "already_used+different@example.org",
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
                f"{email} was unexpectedly authorized even if {used_email} was in DB",
            )
            self.assertIn("email", response.data)

    def test_register_email_with_symbol_plus_must_exclude_self(self) -> None:
        """
        An authenticated user can update its own email, even if the new email
        is similar to the previous one.
        """
        self.client.force_authenticate(user=self.existing_user)

        # TODO
        # The following emails should be considered valid, but currently
        # the built-in validator `UniqueValidator` doesn't exclude the
        # logged user. Oizo: I plan to fix this soon.
        #
        #   - "new_email+@EXAMPLE.org"
        #   - "new_email+TOURNESOL@example.org"

        for current, want in [
            ("new_email@example.org", "new_email+@example.org"),
            ("new_email+@example.org", "NEW_EMAIL+tournesol@example.org"),
            ("NEW_EMAIL+tournesol@example.org", "new_email+different@example.org"),
            ("new_email+different@example.org", "new_email+foo+bar@example.org"),
        ]:
            self.existing_user.email = current
            self.existing_user.save()

            response = self.client.post(
                "/accounts/register-email/",
                {"email": want},
                format="json",
            )
            self.assertEqual(
                response.status_code,
                status.HTTP_200_OK,
                f"{want} was unexpectedly refused even if {current} was in DB",
            )


class AccountsResetPasswordTestCase(TestCase):
    """
    TestCase of the two API:

        /accounts/reset-password/ and
        /accounts/send-reset-password-link/

    Even if these APIs are provided by a third-party package, their default
    behaviours has been customized, and thus need to be tested.
    """

    def test_send_reset_password_link_is_non_case_sensitive(self):
        """
        An anonymous user can ask for a reset password link by using a
        lower/upper variant of its email address.
        """
        client = APIClient()
        UserFactory(
            email="non-sensitive@example.org",
            is_active=True,
        )

        resp = client.post(
            "/accounts/send-reset-password-link/",
            data={
                "login": "NON-sensitive@example.org",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 200, resp.content)

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
