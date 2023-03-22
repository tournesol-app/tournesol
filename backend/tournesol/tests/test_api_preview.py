from unittest.mock import patch

from django.test import TestCase
from PIL import Image
from requests import Response
from rest_framework import status
from rest_framework.test import APIClient

from core.tests.factories.user import UserFactory
from tournesol.entities.video import TYPE_VIDEO
from tournesol.models import Entity


def raise_(exception):
    raise exception


def mock_yt_thumbnail_response(url, timeout=None) -> Response:
    resp = Response()
    resp.status_code = 200
    resp._content = Image.new("1", (1, 1)).tobitmap()
    return resp


class DynamicWebsitePreviewDefaultTestCase(TestCase):
    """
    TestCase of the `DynamicWebsitePreviewDefault` API.
    """

    _user = "username"

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = UserFactory(username=self._user)
        self.preview_url = "/preview/"

    def test_auth_200_get(self):
        """
        An authenticated user must get the default preview image when calling
        the default preview endpoint.
        """
        self.client.force_authenticate(self.user)
        response = self.client.get(f"{self.preview_url}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.headers["Content-Type"], "image/png")
        self.assertEqual(
            response.headers["Content-Disposition"],
            'inline; filename="tournesol_screenshot_og.png"',
        )
        content = b"".join(response.streaming_content)
        self.assertGreater(len(content), 0)

    def test_anon_200_get(self):
        """
        An anonymous user must get the default preview image when calling the
        default preview endpoint.
        """
        response = self.client.get(f"{self.preview_url}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.headers["Content-Type"], "image/png")
        self.assertEqual(
            response.headers["Content-Disposition"],
            'inline; filename="tournesol_screenshot_og.png"',
        )

    def test_anon_200_get_random_url(self):
        """
        An anonymous user must get the default preview image when calling a
        random URL of the preview API.
        """
        response = self.client.get(f"{self.preview_url}random_url")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.headers["Content-Type"], "image/png")
        self.assertEqual(
            response.headers["Content-Disposition"],
            'inline; filename="tournesol_screenshot_og.png"',
        )


class DynamicWebsitePreviewEntityTestCase(TestCase):
    """
    TestCase of the `DynamicWebsitePreviewEntity` API.
    """

    _user = "username"

    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory(username=self._user)

        self.preview_url = "/preview/entities/"
        self.valid_uid = "yt:sDPk-r18sb0"

    @patch("requests.get", mock_yt_thumbnail_response)
    @patch("tournesol.entities.video.VideoEntity.update_search_vector", lambda x: None)
    def test_auth_200_get(self):
        """
        An authenticated user can get the preview image of a video entity existing
        in the database.
        """
        Entity.objects.create(
            uid=self.valid_uid,
            type=TYPE_VIDEO,
            metadata={
                "video_id": self.valid_uid.split(":")[-1],
                "name": "name",
                "uploader": "uploader",
            },
        )

        self.client.force_authenticate(self.user)
        response = self.client.get(f"{self.preview_url}{self.valid_uid}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.headers["Content-Type"], "image/png")
        # The absence of the Content-Disposition header indicates that the
        # default preview image is not returned, as expected in our case. This
        # check is not very robust.
        self.assertNotIn("Content-Disposition", response.headers)

    @patch("requests.get", mock_yt_thumbnail_response)
    @patch("tournesol.entities.video.VideoEntity.update_search_vector", lambda x: None)
    def test_anon_200_get_existing_entity(self):
        """
        An anonymous user can get the preview image of a video entity existing
        in the database.
        """

        Entity.objects.create(
            uid=self.valid_uid,
            type=TYPE_VIDEO,
            metadata={
                "video_id": self.valid_uid.split(":")[-1],
                "name": "name",
                "uploader": "uploader",
            },
        )
        response = self.client.get(f"{self.preview_url}{self.valid_uid}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.headers["Content-Type"], "image/png")
        # The absence of the Content-Disposition header indicates that the
        # default preview image is not returned, as expected in our case. This
        # check is not very robust.
        self.assertNotIn("Content-Disposition", response.headers)

    def test_anon_200_get_non_existing_entity(self):
        """
        An anonymous user must get the default preview image, when requesting
        the preview of a video entity that doesn't exist in the database.
        """
        response = self.client.get(f"{self.preview_url}{self.valid_uid}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.headers["Content-Type"], "image/png")
        self.assertEqual(
            response.headers["Content-Disposition"],
            'inline; filename="tournesol_screenshot_og.png"',
        )

    def test_anon_200_get_invalid_entity_type(self):
        """
        An anonymous user must get the default preview image, when requesting
        the preview of a non-video entity.
        """
        response = self.client.get(f"{self.preview_url}zz:an_invalid_id")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.headers["Content-Type"], "image/png")
        self.assertEqual(
            response.headers["Content-Disposition"],
            'inline; filename="tournesol_screenshot_og.png"',
        )

    @patch("requests.get", lambda x, timeout=None: raise_(ConnectionError))
    @patch("tournesol.entities.video.VideoEntity.update_search_vector", lambda x: None)
    def test_anon_200_get_with_yt_connection_error(self):
        """
        An anonymous user must get the default preview image, if a
        connection error occurs when retrieving the video thumbnail from
        YouTube.
        """
        Entity.objects.create(
            uid=self.valid_uid,
            type=TYPE_VIDEO,
            metadata={
                "video_id": self.valid_uid.split(":")[-1],
                "name": "name",
                "uploader": "uploader",
                "duration": 1337,
            },
        )
        response = self.client.get(f"{self.preview_url}{self.valid_uid}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.headers["Content-Type"], "image/png")
        self.assertEqual(
            response.headers["Content-Disposition"],
            'inline; filename="tournesol_screenshot_og.png"',
        )


class DynamicWebsitePreviewComparisonTestCase(TestCase):
    """
    TestCase of the `DynamicWebsitePreviewComparison` API.
    """

    _user = "username"

    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory(username=self._user)

        self.preview_url = "/preview/comparison"
        self.valid_uid = "yt:sDPk-r18sb0"
        self.valid_uid2 = "yt:VKsekCHBuHI"

    @patch("requests.get", mock_yt_thumbnail_response)
    @patch("tournesol.entities.video.VideoEntity.update_search_vector", lambda x: None)
    def test_auth_200_get(self):
        """
        An authenticated user can get the comparison preview image of 2 video entities existing
        in the database.
        """
        Entity.objects.create(
            uid=self.valid_uid,
            type=TYPE_VIDEO,
            metadata={
                "video_id": self.valid_uid.split(":")[-1],
                "name": "name",
                "uploader": "uploader",
                "duration": 1337,
            },
        )
        Entity.objects.create(
            uid=self.valid_uid2,
            type=TYPE_VIDEO,
            metadata={
                "video_id": self.valid_uid2.split(":")[-1],
                "name": "name2",
                "uploader": "uploader2",
                "duration": 1337,
            },
        )

        self.client.force_authenticate(self.user)
        response = self.client.get(
            self.preview_url, {"uidA": self.valid_uid, "uidB": self.valid_uid2}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.headers["Content-Type"], "image/png")
        # The absence of the Content-Disposition header indicates that the
        # default preview image is not returned, as expected in our case. This
        # check is not very robust.
        self.assertNotIn("Content-Disposition", response.headers)

        # Ensure the URL with a trailing slash is also accepted.
        response = self.client.get(
            f"{self.preview_url}/", {"uidA": self.valid_uid, "uidB": self.valid_uid2}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.headers["Content-Type"], "image/png")
        self.assertNotIn("Content-Disposition", response.headers)

    @patch("requests.get", mock_yt_thumbnail_response)
    @patch("tournesol.entities.video.VideoEntity.update_search_vector", lambda x: None)
    def test_anon_200_get_existing_entities(self):
        """
        An anonymous user can get the comparison preview image of 2 video entities existing
        in the database.
        """

        Entity.objects.create(
            uid=self.valid_uid,
            type=TYPE_VIDEO,
            metadata={
                "video_id": self.valid_uid.split(":")[-1],
                "name": "name",
                "uploader": "uploader",
                "duration": 4242,  # testing for >1 hour
            },
        )
        Entity.objects.create(
            uid=self.valid_uid2,
            type=TYPE_VIDEO,
            metadata={
                "video_id": self.valid_uid2.split(":")[-1],
                "name": "name2",
                "uploader": "uploader2",
                "duration": 1337,  # testing for <1 hour
            },
        )
        response = self.client.get(
            self.preview_url, {"uidA": self.valid_uid, "uidB": self.valid_uid2}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.headers["Content-Type"], "image/png")
        # The absence of the Content-Disposition header indicates that the
        # default preview image is not returned, as expected in our case. This
        # check is not very robust.
        self.assertNotIn("Content-Disposition", response.headers)

    def test_anon_200_get_non_existing_entities(self):
        """
        An anonymous user must get the default preview image, when requesting
        the comparison preview of video entities that don't exist in the database.
        """
        response = self.client.get(
            self.preview_url, {"uidA": self.valid_uid, "uidB": self.valid_uid2}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.headers["Content-Type"], "image/png")
        self.assertEqual(
            response.headers["Content-Disposition"],
            'inline; filename="tournesol_screenshot_og.png"',
        )

    def test_anon_200_get_single_non_existing_entity(self):
        """
        An anonymous user must get the default preview image, when requesting
        the comparison preview of video entities and one of them doesn't exist in the database.
        """
        Entity.objects.create(
            uid=self.valid_uid2,
            type=TYPE_VIDEO,
            metadata={
                "video_id": self.valid_uid2.split(":")[-1],
                "name": "name2",
                "uploader": "uploader2",
                "language": "en",
            },
        )
        response = self.client.get(
            self.preview_url, {"uidA": self.valid_uid, "uidB": self.valid_uid2}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.headers["Content-Type"], "image/png")
        self.assertEqual(
            response.headers["Content-Disposition"],
            'inline; filename="tournesol_screenshot_og.png"',
        )

    def test_anon_200_get_without_required_param(self):
        """
        An anonymous user must get the default preview image, when requesting
        the comparison preview without using the required query parameters.
        """
        # Missing `uidA` parameter.
        response = self.client.get(self.preview_url, {"uidB": self.valid_uid})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.headers["Content-Type"], "image/png")
        self.assertEqual(
            response.headers["Content-Disposition"],
            'inline; filename="tournesol_screenshot_og.png"',
        )

        # Missing `uidB` parameter.
        response = self.client.get(self.preview_url, {"uidA": self.valid_uid2})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.headers["Content-Type"], "image/png")
        self.assertEqual(
            response.headers["Content-Disposition"],
            'inline; filename="tournesol_screenshot_og.png"',
        )

        # Missing both `uidA` and `uidB`.
        response = self.client.get(self.preview_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.headers["Content-Type"], "image/png")
        self.assertEqual(
            response.headers["Content-Disposition"],
            'inline; filename="tournesol_screenshot_og.png"',
        )

    def test_anon_200_get_invalid_entity_type(self):
        """
        An anonymous user must get the default preview image, when requesting
        the preview of a non-video entity.
        """
        Entity.objects.create(
            uid=self.valid_uid,
            type=TYPE_VIDEO,
            metadata={
                "video_id": self.valid_uid.split(":")[-1],
                "name": "name",
                "uploader": "uploader",
                "language": "en",
            },
        )
        response = self.client.get(f"{self.preview_url}{self.valid_uid}/zz:an_invalid_id")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.headers["Content-Type"], "image/png")
        self.assertEqual(
            response.headers["Content-Disposition"],
            'inline; filename="tournesol_screenshot_og.png"',
        )

    @patch("requests.get", lambda x, timeout=None: raise_(ConnectionError))
    @patch("tournesol.entities.video.VideoEntity.update_search_vector", lambda x: None)
    def test_anon_200_get_with_yt_connection_error(self):
        """
        An anonymous user must get the default preview image, if a
        connection error occurs when retrieving the video thumbnail from
        YouTube.
        """
        Entity.objects.create(
            uid=self.valid_uid,
            type=TYPE_VIDEO,
            metadata={
                "video_id": self.valid_uid.split(":")[-1],
                "name": "name",
                "uploader": "uploader",
            },
        )
        Entity.objects.create(
            uid=self.valid_uid2,
            type=TYPE_VIDEO,
            metadata={
                "video_id": self.valid_uid2.split(":")[-1],
                "name": "name2",
                "uploader": "uploader2",
            },
        )
        response = self.client.get(
            self.preview_url, {"uidA": self.valid_uid, "uidB": self.valid_uid2}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.headers["Content-Type"], "image/png")
        self.assertEqual(
            response.headers["Content-Disposition"],
            'inline; filename="tournesol_screenshot_og.png"',
        )
