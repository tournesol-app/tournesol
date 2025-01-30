from functools import cached_property
from pathlib import Path
from typing import List, Optional

import requests
from django.conf import settings

from tournesol.models import Entity


class TournesolBotClient:
    def __init__(self, account):

        credentials = settings.TWITTERBOT_CREDENTIALS
        if account not in credentials:
            raise ValueError(f"No credentials found for {account} account!")

        self.account_cred = credentials[account]
        self.language = self.account_cred["LANGUAGE"]

    @cached_property
    def tweepy_api(self):
        # Client for Twitter API v1.1
        # We need this authentication also because to add media it only works with api v1.1

        import tweepy  # pylint:disable=import-outside-toplevel
        auth = tweepy.OAuth1UserHandler(
            consumer_key=self.account_cred["CONSUMER_KEY"],
            consumer_secret=self.account_cred["CONSUMER_SECRET"],
            access_token=self.account_cred["ACCESS_TOKEN"],
            access_token_secret=self.account_cred["ACCESS_TOKEN_SECRET"],
        )
        return tweepy.API(auth)

    @cached_property
    def tweepy_client(self):
        # Client for Twitter API v2

        import tweepy  # pylint:disable=import-outside-toplevel
        return tweepy.Client(
            consumer_key=self.account_cred["CONSUMER_KEY"],
            consumer_secret=self.account_cred["CONSUMER_SECRET"],
            access_token=self.account_cred["ACCESS_TOKEN"],
            access_token_secret=self.account_cred["ACCESS_TOKEN_SECRET"],
        )

    @property
    def bluesky_handle(self):
        return self.account_cred["ATPROTO_HANDLE"]

    @cached_property
    def atproto_client(self):
        from atproto import Client  # pylint:disable=import-outside-toplevel
        client = Client()
        client.login(
            self.account_cred["ATPROTO_HANDLE"],
            self.account_cred["ATPROTO_PASSWORD"],
        )
        return client

    def create_tweet(self, text: str, media_files: Optional[List[Path]] = None):
        if media_files is None:
            media_ids = []
        else:
            medias = (self.tweepy_api.media_upload(filepath) for filepath in media_files)
            media_ids = [media.media_id for media in medias]

        resp = self.tweepy_client.create_tweet(
            text=text,
            media_ids=media_ids,
        )
        return resp.data["id"]

    def create_bluesky_post(
        self,
        text,
        embed_video: Optional[Entity] = None,
        image_files: Optional[List[Path]] = None,
        image_alts: Optional[List[str]] = None,
    ):
        from atproto import models  # pylint:disable=import-outside-toplevel
        if image_files is None:
            if embed_video is None:
                embed = None
            else:
                preview_response = requests.get(
                    f"https://api.tournesol.app/preview/entities/{embed_video.uid}",
                    timeout=10,
                )
                preview_response.raise_for_status()
                img_data = preview_response.content
                thumb_blob = self.atproto_client.upload_blob(img_data).blob
                embed = models.AppBskyEmbedExternal.Main(
                    external=models.AppBskyEmbedExternal.External(
                        title=embed_video.metadata.get("name", ""),
                        description=embed_video.metadata.get("uploader", ""),
                        uri=f"https://tournesolapp/entities/{embed_video.uid}",
                        thumb=thumb_blob,
                    )
                )
            resp = self.atproto_client.send_post(
                text=text,
                embed=embed,
                langs=[self.language],
            )
        else:
            resp = self.atproto_client.send_images(
                text=text,
                langs=[self.language],
                images=[p.read_bytes() for p in image_files],
                image_alts=image_alts,
            )
        return resp.uri
