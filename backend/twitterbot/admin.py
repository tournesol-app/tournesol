"""
Defines Tournesol twitter bot backend admin interface
"""

from django.contrib import admin
from django.utils.html import format_html
from twitterbot.models.tweeted import TweetedVideo


@admin.register(TweetedVideo)
class TwitterBotAdmin(admin.ModelAdmin):
    list_display = (
        "get_video_id",
        "get_video_name",
        "get_video_uploader",
        "tweet_id",
        "datetime_tweet",
        "bot_name",
        "get_video_link",
    )
    search_fields = ("get_video_name", "get_video_uploader")
    list_filter = ["bot_name"]

    @admin.display(ordering="video__id", description="Video ID")
    def get_video_id(self, obj):
        return obj.video.video_id

    @admin.display(ordering="video__name", description="Video name")
    def get_video_name(self, obj):
        return obj.video.name

    @admin.display(ordering="video__uploader", description="Video uploader")
    def get_video_uploader(self, obj):
        return obj.video.uploader

    @admin.display(
        ordering="video__link_to_youtube", description="Video link to Youtube"
    )
    def get_video_link(self, obj):
        return format_html(
            '<a href="https://youtu.be/{}" target="_blank">Play ▶</a>',
            obj.video.video_id,
        )
