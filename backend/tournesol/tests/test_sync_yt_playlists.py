from datetime import date, timedelta
from unittest import mock

from django.core.management import call_command
from django.db.models import F
from django.test import TestCase, override_settings

from tournesol.models import Entity

from .factories.entity import VideoFactory


class SyncYtPlaylistsCommandTest(TestCase):
    @mock.patch("googleapiclient.discovery.build")
    @override_settings(YOUTUBE_CHANNEL_CREDENTIALS_JSON='{"token": "test-token"}')
    def test_sync_playlist(self, build_mock):
        mocked_playlist_client = build_mock.return_value.playlistItems.return_value

        # The playlist items will listed twice: once for each playlist EN and FR
        mocked_playlist_client.list.return_value.execute.side_effect = [
            {
                # 1 existing item in the EN playlist
                "items": [
                    {
                        "id": "existing-video",
                        "contentDetails": {"videoId": "existing-video"},
                    }
                ],
            },
            {   
                # No item in the FR playlist
                "items": [],
            },
        ]
        mocked_playlist_client.list_next.return_value = None

        # Set up 3 videos that should be inserted into playlist EN
        video = VideoFactory.create_batch(
            3,
            tournesol_score=100,
            metadata__language="en",
            metadata__publication_date=date.today().isoformat(),
        )

        # Set up 1 video that should NOT be inserted into the playlist
        VideoFactory(
            tournesol_score=-10,
            metadata__language="en",
            metadata__publication_date=date.today().isoformat(),
        )

        # Update add_time, to make videos old enough
        Entity.objects.update(add_time=F("add_time") - timedelta(days=10))

        # Run the management command
        call_command("sync_yt_playlists")

        # 1 plaulistItem should be deleted, 3 videos should be inserted
        self.assertEqual(
            mocked_playlist_client.delete.return_value.execute.call_count,
            1,
        )
        self.assertEqual(
            mocked_playlist_client.insert.return_value.execute.call_count,
            3,
        )
