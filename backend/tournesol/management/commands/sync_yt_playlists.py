import json
import logging
import sys

import google.oauth2.credentials
import googleapiclient.discovery
from django.conf import settings
from django.core.management.base import BaseCommand
from googleapiclient.errors import HttpError

from core.utils.time import time_ago
from tournesol.models import Entity, Poll
from tournesol.models.entity import TYPE_VIDEO

PLAYLISTS = [
    {"lang": "en", "playlist_id": "PLXX93NlSmUpayYeaNvKaeftX_QwEei3fU"},
    {"lang": "fr", "playlist_id": "PLXX93NlSmUpZkR9NaBXMaPlPalESb5tDv"},
]


class Command(BaseCommand):
    help = "Sync Tournesol recommendations with public playlists on Tournesol Youtube channel"

    def get_top_recent_videos(self, language):
        """
        Get top recent video that should be present in the YouTube playlist
        for a certain language.
        """

        return (
            Entity.objects.filter(
                type=TYPE_VIDEO,
                add_time__lte=time_ago(days=3),
                metadata__publication_date__gte=time_ago(days=60).isoformat(),
                metadata__language=language,
            )
            .filter_safe_for_poll(Poll.default_poll())
            .order_by("all_poll_ratings__tournesol_score")
        )

    def get_existing_items(self, yt_client, playlist_id):
        items_dict = {}
        items_client = yt_client.playlistItems()
        request = items_client.list(
            playlistId=playlist_id,
            part="contentDetails",
            maxResults=50,
        )

        while request is not None:
            response = request.execute()
            for item in response["items"]:
                items_dict[item["contentDetails"]["videoId"]] = item["id"]
            request = items_client.list_next(request, response)

        return items_dict

    def insert_video_in_playlist(self, yt_client, playlist_id, video_id):
        try:
            yt_client.playlistItems().insert(
                part="snippet",
                body={
                    "snippet": {
                        "playlistId": playlist_id,
                        "position": 0,
                        "resourceId": {
                            "kind": "youtube#video",
                            "videoId": video_id,
                        },
                    }
                },
            ).execute()
        except HttpError as e:
            if e.status_code == 400:
                # The video may no longer be available on Youtube
                logging.warning(
                    "Failed to insert video_id '%s' in playlist '%s'",
                    video_id,
                    playlist_id,
                    exc_info=True,
                )
            else:
                raise

    def sync_playlist(self, yt_client, playlist_id, lang):
        videos_to_publish = {v.video_id: v for v in self.get_top_recent_videos(lang)}
        existing_items = self.get_existing_items(yt_client, playlist_id)

        video_ids_to_delete = set(existing_items.keys()) - set(videos_to_publish.keys())
        for video_id in video_ids_to_delete:
            yt_client.playlistItems().delete(id=existing_items[video_id]).execute()

        video_ids_to_insert = set(videos_to_publish.keys()) - set(existing_items.keys())
        # Insert in order of increasing tournesol_score
        # to put videos with higher scores at the top of playlist
        for video_id in videos_to_publish:
            if video_id in video_ids_to_insert:
                self.insert_video_in_playlist(
                    yt_client, playlist_id=playlist_id, video_id=video_id
                )

    def handle(self, *args, **options):
        if not settings.YOUTUBE_CHANNEL_CREDENTIALS_JSON:
            self.stderr.write(
                "Impossible to sync YouTube playlists. "
                "`YOUTUBE_CHANNEL_CREDENTIALS_JSON` is not configured."
            )
            self.stderr.write(
                "To get these credentials, follow the instructions "
                "in scripts/youtube/youtube_channel_oauth_flow.py"
            )
            return sys.exit(1)

        channel_credentials = json.loads(settings.YOUTUBE_CHANNEL_CREDENTIALS_JSON)
        credentials = google.oauth2.credentials.Credentials(**channel_credentials)
        yt_client = googleapiclient.discovery.build("youtube", "v3", credentials=credentials)
        for playlist in PLAYLISTS:
            self.sync_playlist(yt_client, playlist["playlist_id"], playlist["lang"])
