
from unittest.mock import patch

from django.test import TestCase

from core.utils.time import time_ago
from tournesol.tests.factories.entity import VideoFactory

from .video import VideoEntity


@patch("tournesol.utils.api_youtube.get_video_metadata")
class VideoEntityTypeTestCase(TestCase):

    def test_never_refreshed_needs_to_be_refreshed(self, mock_request):
        video = VideoFactory(last_metadata_request_at=None)
        self.assertTrue(VideoEntity(video).metadata_needs_to_be_refreshed())

    def test_refreshed_31_days_ago_needs_to_be_refreshed(self, mock_request):
        video = VideoFactory(last_metadata_request_at=time_ago(days=31))
        self.assertTrue(VideoEntity(video).metadata_needs_to_be_refreshed())

    def test_refreshed_now_neednt_be_refreshed(self, mock_request):
        video = VideoFactory(last_metadata_request_at=time_ago(seconds=1))
        self.assertFalse(VideoEntity(video).metadata_needs_to_be_refreshed())

    def test_refreshed_10_minutes_ago_neednt_be_refreshed(self, mock_request):
        video = VideoFactory(last_metadata_request_at=time_ago(minutes=10))
        self.assertFalse(VideoEntity(video).metadata_needs_to_be_refreshed())

    def test_published_15_minutes_ago_needs_to_be_refreshed(self, mock_request):
        video = VideoFactory(
            metadata__publication_date=time_ago(minutes=15).isoformat(),
            last_metadata_request_at=time_ago(minutes=10)
        )
        self.assertTrue(VideoEntity(video).metadata_needs_to_be_refreshed())

    def test_published_15_days_ago_needs_to_be_refreshed(self, mock_request):
        video = VideoFactory(
            metadata__publication_date=time_ago(days=15).isoformat(),
            last_metadata_request_at=time_ago(days=10)
        )
        self.assertTrue(VideoEntity(video).metadata_needs_to_be_refreshed())

    def test_published_15_days_ago_neednt_to_be_refreshed(self, mock_request):
        video = VideoFactory(
            metadata__publication_date=time_ago(days=15).isoformat(),
            last_metadata_request_at=time_ago(days=5)
        )
        self.assertFalse(VideoEntity(video).metadata_needs_to_be_refreshed())

    def test_metadata_views_stored_on_64bits(self, mock_request):
        video = VideoFactory(metadata__views=9_000_000_000)
        self.assertEqual(video.metadata["views"], 9_000_000_000)
