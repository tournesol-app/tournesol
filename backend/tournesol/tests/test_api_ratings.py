from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from core.models import User

class RatingApi(TestCase):
    """
    TestCase of the Rating API.

    """
    _user = "user_with_one_video"

    def setUp(self):
        user1 = User.objects.create(username=self._user)


    def test_try_to_create(self):
        factory = APIClient()
        user = User.objects.get(username=self._user)
        factory.force_authenticate(user=user)
        response = factory.post(
            "/users/me/contributor_ratings/",
            {'video_id':'NeADlWSDFAQ'},
            args=[user.username],
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
