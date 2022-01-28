"""
Models for Tournesol twitter bot already tweeted videos
"""

from django.db import models
from tournesol.models import Video


BOT_NAME = [
    ("EN", "@TournesolBot"),
    ("FR", "@TournesolBotFR"),
]


class TweetedVideo(models.Model):
    """One tweeted video."""

    video = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        related_name="video",
        help_text="Tweeted video",
    )

    tweet_id = models.CharField(
        null=False,
        max_length=22,
        help_text=f"Tweet ID from Twitter URL",
    )

    datetime_tweet = models.DateTimeField(
        auto_now_add=True,
        help_text="Time when the video was tweeted",
        null=True,
        blank=True,
    )

    bot_name = models.CharField(
        null=True,
        blank=True,
        max_length=10,
        help_text="Name of the twitter bot",
        choices=BOT_NAME,
    )

    def __str__(self):
        return f"{self.video.video_id} tweeted at {self.datetime_tweet}"
