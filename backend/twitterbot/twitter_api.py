from functools import cached_property
from pathlib import Path
from typing import List, Optional

from django.conf import settings


class TwitterBot:
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
