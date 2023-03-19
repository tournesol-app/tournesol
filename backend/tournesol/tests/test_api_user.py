from unittest.mock import patch

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from core.models import EmailDomain, User
from core.tests.factories.user import UserFactory
from tournesol.throttling import GlobalEmailScopeThrottle


class UserDeletionTestCase(TestCase):
    def test_delete_anonymous_401(self):
        """
        Account deletion requires authentication
        """
        client = APIClient()
        response = client.delete("/users/me/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_my_user(self):
        """
        Delete the current user
        """
        client = APIClient()
        user = UserFactory()
        client.force_authenticate(user=user)

        response = client.delete("/users/me/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(username=user.username, is_active=True).exists())

        user.refresh_from_db()
        self.assertRegex(user.email, r".*@deleted.invalid")


class UserRegistrationTest(TestCase):
    def test_register_user(self):
        """
        Register user with minimal payload
        """
        client = APIClient()
        response = client.post("/accounts/register/", data={
            "username": "test-user",
            "password": "a_safe_password",
            "password_confirm": "a_safe_password",
            "email": "me@example.com",
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_register_username_me_is_reserved(self):
        """
        Register username 'me' should not be possible
        """
        client = APIClient()
        response = client.post("/accounts/register/", data={
            "username": "me",
            "password": "a_safe_password",
            "password_confirm": "a_safe_password",
            "email": "me@example.com",
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_email_address_as_username_is_rejected(self):
        client = APIClient()
        response = client.post("/accounts/register/", data={
            "username": "me@example.com",
            "password": "a_safe_password",
            "password_confirm": "a_safe_password",
            "email": "me@example.com",
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_register_with_existing_email(self):
        client = APIClient()
        response = client.post("/accounts/register/", data={
            "username": "test-user",
            "password": "a_safe_password",
            "password_confirm": "a_safe_password",
            "email": "me@example.com",
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = client.post("/accounts/register/", data={
            "username": "test-user2",
            "password": "a_safe_password",
            "password_confirm": "a_safe_password",
            "email": "me@example.com",
        }, format="json")
        self.assertContains(response,
            text="email address already exists",
            status_code=400
        )

    @patch.object(GlobalEmailScopeThrottle, "get_rate", new=lambda *_: "2/min")
    def test_register_throttle(self):
        """
        Throttle should be triggered on the 3rd request
        """
        client = APIClient()

        response = client.post("/accounts/register/", data={}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = client.post("/accounts/register/", data={}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = client.post("/accounts/register/", data={}, format="json")
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)


class UserRegisterNewEmailTest(TestCase):
    def setUp(self) -> None:
        self.user1 = UserFactory(email="user1@example.com")
        self.user2 = UserFactory(email="user2@example.com")
        self.client = APIClient()
        self.client.force_authenticate(self.user1)

    def test_ask_for_email_update(self):
        resp = self.client.post("/accounts/register-email/", data={
            "email": "new.email@example.com"
        }, format="json")
        self.assertEqual(resp.status_code, 200)
        self.user1.refresh_from_db()
        # Email does not change before the verification link is clicked
        self.assertEqual(self.user1.email, "user1@example.com")

    def test_cannot_submit_existing_email(self):
        resp = self.client.post("/accounts/register-email/", data={
            "email": "user2@example.com"
        }, format="json")
        self.assertContains(
            resp,
            text="email address already exists",
            status_code=400,
        )


class AccountProfileTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user1 = UserFactory(username="user1", email="user1@example.com")
        EmailDomain.objects.filter(domain="@example.com").update(status=EmailDomain.STATUS_ACCEPTED)
        self.user2 = UserFactory(username="user2", email="user2@rejected.test")
        EmailDomain.objects.filter(domain="@rejected.test").update(status=EmailDomain.STATUS_REJECTED)

    def test_user_profile(self):
        self.client.force_authenticate(self.user1)
        resp = self.client.get("/accounts/profile/")

        self.assertEqual(resp.status_code, 200)
        profile_data = resp.json()
        self.assertEqual(profile_data["username"], "user1")
        self.assertEqual(profile_data["email"], "user1@example.com")
        self.assertEqual(profile_data["is_trusted"], True) # Email domain is accepted

    def test_user_profile_with_rejected_domain(self):
        self.client.force_authenticate(self.user2)
        resp = self.client.get("/accounts/profile/")

        self.assertEqual(resp.status_code, 200)
        profile_data = resp.json()
        self.assertEqual(profile_data["username"], "user2")
        self.assertEqual(profile_data["email"], "user2@rejected.test")
        self.assertEqual(profile_data["is_trusted"], False) # Email domain is rejected

    def test_update_username(self):
        self.client.force_authenticate(self.user1)
        resp = self.client.patch("/accounts/profile/", data={"username": "new_user1"}, format="json")

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["username"], "new_user1")
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.username, "new_user1")

    def test_username_validation_on_update(self):
        self.client.force_authenticate(self.user1)
        resp = self.client.patch("/accounts/profile/", data={"username": "user1@example.com"}, format="json")
        self.assertEqual(resp.status_code, 400)
