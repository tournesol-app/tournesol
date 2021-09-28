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
