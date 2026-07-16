"""
All test cases of the Bilibili API utilities.
"""
from unittest.mock import patch

import requests
from django.test import SimpleTestCase

from tournesol.utils.api_bilibili import get_bilibili_video_metadata
from tournesol.utils.api_youtube import VideoNotFound


@patch("tournesol.utils.api_bilibili.get_bilibili_video_details")
class GetBilibiliVideoMetadataTestCase(SimpleTestCase):

    def test_metadata_mapping(self, mock_details):
        mock_details.return_value = {
            "code": 0,
            "message": "0",
            "data": {
                "bvid": "BV1GJ411x7h7",
                "title": "视频标题",
                "desc": "视频简介",
                "pubdate": 1577836800,
                "duration": 213,
                "pic": "http://i0.hdslb.com/bfs/archive/example.jpg",
                "owner": {"mid": 928123, "name": "UP主"},
                "stat": {"view": 320000},
            },
        }

        metadata = get_bilibili_video_metadata("BV1GJ411x7h7", compute_language=False)

        self.assertEqual(metadata["source"], "bilibili")
        self.assertEqual(metadata["name"], "视频标题")
        self.assertEqual(metadata["description"], "视频简介")
        self.assertEqual(metadata["publication_date"], "2020-01-01T00:00:00+00:00")
        self.assertEqual(metadata["duration"], 213)
        self.assertEqual(metadata["views"], 320000)
        self.assertEqual(metadata["uploader"], "UP主")
        self.assertEqual(metadata["channel_id"], "928123")
        self.assertEqual(
            metadata["thumbnail_url"], "http://i0.hdslb.com/bfs/archive/example.jpg"
        )
        self.assertIsNone(metadata["language"])

    def test_video_not_found(self, mock_details):
        mock_details.return_value = {"code": -404, "message": "啥都木有", "data": None}

        with self.assertRaises(VideoNotFound):
            get_bilibili_video_metadata("BV1GJ411x7h7", compute_language=False)

    def test_unexpected_error_code_returns_no_metadata(self, mock_details):
        mock_details.return_value = {"code": -509, "message": "请求过于频繁", "data": None}

        metadata = get_bilibili_video_metadata("BV1GJ411x7h7", compute_language=False)
        self.assertEqual(metadata, {})

    def test_request_error_returns_no_metadata(self, mock_details):
        mock_details.side_effect = requests.RequestException

        metadata = get_bilibili_video_metadata("BV1GJ411x7h7", compute_language=False)
        self.assertEqual(metadata, {})
