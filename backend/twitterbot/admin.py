"""
The Tournesol Twitter Bot admin interface.
"""

from urllib.parse import urljoin

from django.conf import settings
from django.contrib import admin
from django.utils.html import format_html

from .models.tweeted import TweetInfo


@admin.register(TweetInfo)
class TwitterBotAdmin(admin.ModelAdmin):
    """Twitter Bot Admin class"""

    raw_id_fields = ("video",)
    readonly_fields = ("datetime_tweet",)

    list_display = (
        "video",
        "get_video_name",
        "get_video_uploader",
        "bot_name",
        "datetime_tweet",
        "get_twitter_link",
        "get_video_link",
        "tweet_id",
    )
    search_fields = ("video__uid", "video__metadata__name", "video__metadata__uploader")
    list_filter = ["bot_name"]

    @staticmethod
    @admin.display(description="URL of the tweet")
    def get_twitter_link(obj):
        """Return the URI of the tweet."""
        return format_html(
            '<a href="https://twitter.com/{}/status/{}" target="_blank">Tweet</a>',
            obj.bot_name,
            obj.tweet_id,
        )

    @staticmethod
    @admin.display(ordering="video__metadata__name", description="Video name")
    def get_video_name(obj):
        """Return the video name."""
        return obj.video.metadata.get("name")

    @staticmethod
    @admin.display(ordering="video__metadata__uploader", description="Video uploader")
    def get_video_uploader(obj):
        """Return the video uploader."""
        return obj.video.metadata.get("uploader")

    @staticmethod
    @admin.display(description="Tournesol link")
    def get_video_link(obj):
        """
        Return the Tournesol front end URI of the video, in the poll `videos`.
        """
        video_uri = urljoin(
            settings.REST_REGISTRATION_MAIN_URL, f"entities/yt:{obj.video.video_id}"
        )
        return format_html('<a href="{}" target="_blank">Play ▶</a>', video_uri)
