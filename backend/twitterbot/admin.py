"""
Defines Tournesol twitter bot backend admin interface
"""

from django.contrib import admin
from django.utils.html import format_html

from .models.tweeted import TweetedVideo


@admin.register(TweetedVideo)
class TwitterBotAdmin(admin.ModelAdmin):
    """Twitter Bot Admin class"""

    raw_id_fields = ("video",)
    readonly_fields = ("datetime_tweet",)

    list_display = (
        "video",
        "get_video_name",
        "get_video_uploader",
        "tweet_id",
        "datetime_tweet",
        "bot_name",
        "get_video_link",
    )
    search_fields = ("video__uid", "video__metadata__name", "video__metadata__uploader")
    list_filter = ["bot_name"]

    @staticmethod
    @admin.display(ordering="video__metadata__name", description="Video name")
    def get_video_name(obj):
        """Returns video name"""
        return obj.video.metadata.get("name")

    @staticmethod
    @admin.display(ordering="video__metadata__uploader", description="Video uploader")
    def get_video_uploader(obj):
        """Returns video uploader"""
        return obj.video.metadata.get("uploader")

    @staticmethod
    @admin.display(description="Video link to Youtube")
    def get_video_link(obj):
        """Returns video link to Youtube"""

        return format_html(
            '<a href="https://youtu.be/{}" target="_blank">Play ▶</a>',
            obj.video.video_id,
        )
