from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from core.models import User


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
        username = "test-user"
        user = User.objects.create(username=username)
        client.force_authenticate(user=user)

        response = client.delete("/users/me/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(username=username).exists())


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

class UserRegisterNewEmailTest(TestCase):
    def setUp(self) -> None:
        self.user1 = User.objects.create_user(username="user1", email="user1@example.com")
        self.user2 = User.objects.create_user(username="user2", email="user2@example.com")
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
        self.assertContains(resp,
            text="email address already exists",
            status_code=400
        )
