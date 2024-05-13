from unittest.mock import patch

from django.core.cache import cache
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from core.tests.factories.user import UserFactory


class ThrottlingTestCase(TestCase):
    """
    TestCase of the API throttling policy.

    This test case doesn't test if the throttling works, it's the
    responsibility of the Django REST framework. Instead, it ensures that
    sensitive views have been configured to use either the
    `ScopedRateThrottle` class, or a custom one.
    """

    def setUp(self):
        self.user = UserFactory()
        cache.clear()

    @patch("rest_framework.throttling.ScopedRateThrottle.get_rate")
    def test_throttling_on_public_comparisons(self, mock):
        """
        Ensure `ExportPublicComparisonsView` has been configured with a
        throttle_scope.
        """
        mock.return_value = "1/min"

        client = APIClient()

        response = client.get("/exports/comparisons/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = client.get("/exports/comparisons/")
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    @patch("rest_framework.throttling.ScopedRateThrottle.get_rate")
    def test_throttling_on_personal_export_all(self, mock):
        """
        Ensure `ExportAllView` has been configured with a
        throttle_scope.
        """
        mock.return_value = "1/min"

        client = APIClient()

        client.force_authenticate(user=self.user)

        response = client.get("/users/me/exports/all/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = client.get("/users/me/exports/all/")
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    @patch("rest_framework.throttling.ScopedRateThrottle.get_rate")
    def test_throttling_on_personal_export_comparisons(self, mock):
        """
        Ensure `ExportComparisonsView` has been configured with a
        throttle_scope.
        """
        mock.return_value = "1/min"

        client = APIClient()

        client.force_authenticate(user=self.user)

        response = client.get("/users/me/exports/comparisons/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = client.get("/users/me/exports/comparisons/")
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    @patch("tournesol.throttling.PostScopeRateThrottle.get_rate")
    def test_throttling_on_video_post(self, mock):
        """
        Ensure `ExportComparisonsView` has been configured with the custom
        `PostScopeRateThrottle` class.
        """
        mock.return_value = "1/min"

        client = APIClient()

        client.force_authenticate(user=self.user)

        # POST requests must be throttled
        response = client.post("/video/", {"video_id": "NeADlWSDFAQ"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = client.post("/video/", {"video_id": "videoid2abc"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
