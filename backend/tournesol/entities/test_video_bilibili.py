import re
from unittest.mock import patch

from django.test import SimpleTestCase, TestCase

from tournesol.serializers.metadata import VideoMetadata
from tournesol.tests.factories.entity import BilibiliVideoFactory, VideoFactory

from .video import BILIBILI_UID_NAMESPACE, YOUTUBE_UID_NAMESPACE, VideoEntity


class BilibiliUidRegexTestCase(SimpleTestCase):

    def test_uid_regex_matches_bilibili_uid(self):
        regex = VideoEntity.get_uid_regex(BILIBILI_UID_NAMESPACE)
        self.assertTrue(re.fullmatch(regex, "bili:BV1GJ411x7h7"))

    def test_uid_regex_rejects_invalid_bilibili_id(self):
        regex = VideoEntity.get_uid_regex(BILIBILI_UID_NAMESPACE)
        # "0", "I", "O" and "l" are not part of the base58 alphabet
        self.assertIsNone(re.fullmatch(regex, "bili:BV0GJ411x7hI"))
        # A YouTube video id is not a valid Bilibili video id
        self.assertIsNone(re.fullmatch(regex, "bili:NeADlWSDFAQ"))

    def test_uid_namespaces_are_not_interchangeable(self):
        yt_regex = VideoEntity.get_uid_regex(YOUTUBE_UID_NAMESPACE)
        bilibili_regex = VideoEntity.get_uid_regex(BILIBILI_UID_NAMESPACE)
        self.assertIsNone(re.fullmatch(yt_regex, "yt:BV1GJ411x7h7"))
        self.assertIsNone(re.fullmatch(bilibili_regex, "yt:NeADlWSDFAQ"))


class VideoMetadataVideoIdTestCase(SimpleTestCase):

    def test_video_id_accepts_youtube_id(self):
        serializer = VideoMetadata(data={"video_id": "NeADlWSDFAQ"})
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_video_id_accepts_bilibili_id(self):
        serializer = VideoMetadata(data={"video_id": "BV1GJ411x7h7"})
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_video_id_rejects_invalid_id(self):
        # Note: an 11-symbol Bilibili-looking id such as "BV1GJ411x7h" cannot
        # be rejected, as it is undistinguishable from a YouTube video id.
        for video_id in ["", "BV1GJ411x7", "BV1GJ411x7h7x", "invalid id!"]:
            serializer = VideoMetadata(data={"video_id": video_id})
            self.assertFalse(serializer.is_valid())


@patch("tournesol.utils.api_bilibili.get_bilibili_video_metadata")
@patch("tournesol.utils.api_youtube.get_video_metadata")
class VideoEntityMetadataSourceTestCase(TestCase):

    def test_update_metadata_uses_bilibili_api_for_bilibili_uid(
        self, mock_youtube, mock_bilibili
    ):
        mock_bilibili.return_value = {"views": 42}
        video = BilibiliVideoFactory()

        VideoEntity(video).update_metadata_field()

        mock_bilibili.assert_called_once()
        mock_youtube.assert_not_called()
        self.assertEqual(video.metadata["views"], 42)

    def test_update_metadata_uses_youtube_api_for_youtube_uid(
        self, mock_youtube, mock_bilibili
    ):
        mock_youtube.return_value = {"views": 42}
        video = VideoFactory()

        VideoEntity(video).update_metadata_field()

        mock_youtube.assert_called_once()
        mock_bilibili.assert_not_called()
        self.assertEqual(video.metadata["views"], 42)
