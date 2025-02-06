"""
Models related to the Twitter bot.
"""
import re

from django.db import models

from tournesol.models import Entity

BOT_NAME = [
    ("@TournesolBot", "@TournesolBot"),
    ("@TournesolBotFR", "@TournesolBotFR"),
]


class TweetInfo(models.Model):
    """One tweeted video."""

    video = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name="tweets",
        help_text="Posted video",
    )

    tweet_id = models.CharField(
        null=True,
        default=None,
        max_length=22,
        help_text="Tweet ID from Twitter URL",
    )

    atproto_uri = models.CharField(
        null=True,
        default=None,
        max_length=255,
        help_text="URI of the post on the AT protocol network",
    )

    datetime_tweet = models.DateTimeField(
        auto_now_add=True,
        help_text="Time when the video was posted",
        null=True,
        blank=True,
    )

    bot_name = models.CharField(
        null=True,
        blank=True,
        max_length=200,
        help_text="Name of the bot",
        choices=BOT_NAME,
    )

    def __str__(self):
        return f"{self.video.uid} posted at {self.datetime_tweet}"

    @property
    def tweet_url(self):
        if not self.tweet_id:
            return None
        return f"https://twitter.com/{self.bot_name}/status/{self.tweet_id}"

    @property
    def bluesky_url(self):
        if not self.atproto_uri:
            return None
        match = re.match(
            r"at://(?P<authority>.+)/(?P<collection>.+)/(?P<key>.+)",
            self.atproto_uri,
        )
        if not match or match.group("collection") != "app.bsky.feed.post":
            return None
        return f"https://bsky.app/profile/{match.group('authority')}/post/{match.group('key')}"

    @property
    def message_url(self):
        bluesky_url = self.bluesky_url
        if bluesky_url:
            return self.bluesky_url
        return self.tweet_url
