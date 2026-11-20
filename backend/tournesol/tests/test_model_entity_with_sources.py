from unittest.mock import patch

from django.test import TestCase

from tournesol.models import EntitySource, EntitySourceLink
from tournesol.tests.factories.entity import VideoFactory
from tournesol.tests.factories.subscription import EntitySourceFactory

CHANNEL_ID = "UCH8TsmKEX_PR4jxsg2W3vOg"
CHANNEL_UID = f"yt:{CHANNEL_ID}"
OTHER_CHANNEL_ID = "UC1EacOJoqsKaYxaDomTCTEQ"
OTHER_CHANNEL_UID = f"yt:{OTHER_CHANNEL_ID}"

CHANNEL_METADATA = {
    "name": "Tournesol",
    "thumbnail": "https://yt3.ggpht.com/medium",
    "custom_url": "@tournesol",
}


@patch("tournesol.utils.api_youtube.get_channel_metadata", return_value=CHANNEL_METADATA)
class EntitySourceSyncTestCase(TestCase):
    def test_creating_video_must_create_its_channel(self, mock_get_channel_metadata):
        self.assertEqual(EntitySource.objects.count(), 0)

        video = VideoFactory(metadata__channel_id=CHANNEL_ID)

        self.assertEqual(EntitySource.objects.count(), 1)
        self.assertEqual([source.uid for source in video.sources.all()], [CHANNEL_UID])
        self.assertEqual(video.sources.get().metadata, CHANNEL_METADATA)
        mock_get_channel_metadata.assert_called_once_with(CHANNEL_ID)

    def test_creating_video_must_link_it_to_existing_channel(
        self, mock_get_channel_metadata
    ):
        source = EntitySourceFactory(uid=CHANNEL_UID)
        video = VideoFactory(metadata__channel_id=CHANNEL_ID)

        self.assertEqual(list(video.sources.all()), [source])
        self.assertEqual(EntitySource.objects.count(), 1)

        # The existing channel metadata should be not refreshed.
        mock_get_channel_metadata.assert_not_called()

    def test_updating_metadata_channel_must_update_video_sources(self, _mock_get_channel_metadata):
        video = VideoFactory(metadata__channel_id=CHANNEL_ID)

        video.metadata["channel_id"] = OTHER_CHANNEL_ID
        video.save(update_fields=["metadata"])

        self.assertEqual([source.uid for source in video.sources.all()], [OTHER_CHANNEL_UID])
        self.assertTrue(EntitySource.objects.filter(uid=CHANNEL_UID).exists())

    def test_removing_metadata_channel_must_remove_related_sources(self, _mock_get_channel_metadata):
        video = VideoFactory(metadata__channel_id=CHANNEL_ID)
        n_sources = EntitySource.objects.count()

        video.metadata["channel_id"] = None
        video.save(update_fields=["metadata"])

        self.assertFalse(video.sources.exists())
        # The channel is unlinked, but not deleted.
        self.assertEqual(EntitySource.objects.count(), n_sources)

    def test_not_updating_metadata_must_not_update_video_sources(
        self, _mock_get_channel_metadata
    ):
        video = VideoFactory(metadata__channel_id=CHANNEL_ID)
        self.assertEqual(video.sources.count(), 1)
        video.metadata = {}

        with self.assertNumQueries(1):
            video.save(update_fields=["last_metadata_request_at"])

        self.assertEqual(video.sources.count(), 1)

    def test_not_updating_metadata_channel_must_not_update_video_sources(self, mock_get_channel_metadata):
        video = VideoFactory(metadata__channel_id=CHANNEL_ID)
        link = EntitySourceLink.objects.get(entity=video)

        video.save(update_fields=["metadata"])

        self.assertEqual(list(EntitySourceLink.objects.filter(entity=video)), [link])
        mock_get_channel_metadata.assert_called_once()

    def test_channel_missing_on_youtube_is_not_linked(self, mock_get_channel_metadata):
        # pylint: disable=import-outside-toplevel
        from tournesol.utils.api_youtube import ChannelNotFound

        mock_get_channel_metadata.side_effect = ChannelNotFound

        video = VideoFactory(metadata__channel_id=CHANNEL_ID)

        self.assertFalse(video.sources.exists())
        self.assertFalse(EntitySource.objects.exists())

    def test_video_without_channel_has_no_source(self, mock_get_channel_metadata):
        video = VideoFactory()

        self.assertFalse(video.sources.exists())
        mock_get_channel_metadata.assert_not_called()
