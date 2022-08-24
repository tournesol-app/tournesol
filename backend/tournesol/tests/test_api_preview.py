from PIL import Image
from unittest.mock import patch

from django.test import TestCase
from requests import Response
from rest_framework import status
from rest_framework.test import APIClient

from core.tests.factories.user import UserFactory
from tournesol.entities.video import TYPE_VIDEO
from tournesol.models import Entity


def mock_yt_thumbnail_response(url) -> Response:
    resp = Response()
    resp.status_code = 200
    resp._content = Image.new("1", (1, 1)).tobitmap()
    return resp


class DynamicWebsitePreviewEntityTestCase(TestCase):
    """
    TestCase of the `DynamicWebsitePreviewEntity` API.
    """

    _user = "username"

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = UserFactory(username=self._user)

        self.preview_url = "/preview/entities/"
        self.valid_uid = "yt:sDPk-r18sb0"

    def test_auth_200_get(self) -> None:
        self.client.force_authenticate(self.user)
        response = self.client.get(f"{self.preview_url}{self.valid_uid}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.headers["Content-Type"], "image/png")
        self.assertEqual(
            response.headers["Content-Disposition"],
            'inline; filename="tournesol_screenshot_og.png"'
        )

    @patch('requests.get', mock_yt_thumbnail_response)
    @patch('tournesol.entities.video.VideoEntity.update_search_vector', lambda x: None)
    def test_anon_200_get_existing_entity(self) -> None:
        """
        An anonymous user can get the preview image of a video entity existing
        in the database.
        """

        Entity.objects.create(
            uid=self.valid_uid,
            type=TYPE_VIDEO,
            metadata={
                "video_id":  self.valid_uid.split(":")[-1],
                "name": "name",
                "uploader": "uploader"

            }
        )
        response = self.client.get(f"{self.preview_url}{self.valid_uid}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.headers["Content-Type"], "image/png")

        # The absence of the Content-Disposition header indicates that the
        # default preview image is not returned, as expected in our case. This
        # check is not very robust.
        self.assertNotIn("Content-Disposition", response.headers)

    def test_anon_200_get_non_existing_entity(self) -> None:
        """
        An anonymous user must get the default preview image, when requesting
        the preview of a video entity that doesn't exist in the database.
        """
        response = self.client.get(f"{self.preview_url}{self.valid_uid}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.headers["Content-Type"], "image/png")
        self.assertEqual(
            response.headers["Content-Disposition"],
            'inline; filename="tournesol_screenshot_og.png"'
        )

    def test_anon_200_get_invalid_entity_type(self) -> None:
        """
        An anonymous user must get the default preview image, when requesting
        the preview of a non-video entity.
        """
        response = self.client.get(f"{self.preview_url}zz:an_invalid_id")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.headers["Content-Type"], "image/png")
        self.assertEqual(
            response.headers["Content-Disposition"],
            'inline; filename="tournesol_screenshot_og.png"'
        )
