"""
Models for Tournesol twitter bot already tweeted videos
"""

from django.db import models
from django.core.validators import RegexValidator
from django.utils.html import format_html

from core.utils.models import WithEmbedding, WithFeatures
from core.utils.constants import TWITTER_TWEET_ID_ID_REGEX
from django.utils.html import format_html

from languages.languages import LANGUAGES


class TweetedVideo(models.Model, WithFeatures, WithEmbedding):
    """One tweeted video."""

    video = models.ForeignKey(
        "Video",
        on_delete=models.CASCADE,
        related_name="tweeted_video",
        help_text="Tweeted video",
    )

    tweet_id_regex = RegexValidator(
        TWITTER_TWEET_ID_ID_REGEX, f"Video ID must match {TWITTER_TWEET_ID_ID_REGEX}"
    )

    tweet_id = models.CharField(
        max_length=20,
        unique=True,
        help_text=f"Tweet ID from Twitter URL, matches {TWITTER_TWEET_ID_ID_REGEX}",
        validators=[tweet_id_regex],
    )

    datetime_tweet = models.DateTimeField(
        auto_now_add=True,
        help_text="Time when the video was tweeted",
        null=True,
        blank=True,
    )

    language = models.CharField(
        null=True,
        blank=True,
        max_length=10,
        help_text="Language of the video tweeted, correspond to the language of the twitter bot",
        choices=LANGUAGES,
    )

    info = models.TextField(
        null=True, blank=True, help_text="Additional information (json)"
    )

    def __str__(self):
        return f"{self.video.video_id} tweeted at {self.datetime_tweet}"

    def link_to_youtube(self):
        return format_html(
            '<a href="https://youtu.be/{}" target="_blank">Play ▶</a>',
            self.video.video_id,
        )
