from rest_framework import serializers

from tournesol.utils.constants import YOUTUBE_VIDEO_ID_REGEX


class VideoMetadata(serializers.Serializer):
    source = serializers.CharField(allow_blank=True, default="")
    video_id = serializers.RegexField(rf"^({YOUTUBE_VIDEO_ID_REGEX})$")
    name = serializers.CharField(allow_blank=True, default="")
    description = serializers.CharField(allow_blank=True, default="")
    uploader = serializers.CharField(allow_blank=True, default="")
    channel_id = serializers.CharField(allow_null=True, default=None)
    publication_date = serializers.DateTimeField(allow_null=True, default=None)
    duration = serializers.IntegerField(
        allow_null=True,
        default=None,
        help_text="Duration in seconds. May be null (e.g on live streams)"
    )
    views = serializers.IntegerField(allow_null=True, default=None)
    language = serializers.CharField(allow_null=True, default=None)
    tags = serializers.ListField(child=serializers.CharField(), default=list)
    is_unlisted = serializers.BooleanField(default=False)


class CandidateMetadata(serializers.Serializer):
    name = serializers.CharField()
    image_url = serializers.URLField(allow_null=True, default=None)
    frwiki_title = serializers.CharField(allow_null=True, default=None)
    website_url = serializers.URLField(allow_null=True, default=None)
    youtube_channel_id = serializers.CharField(allow_null=True, default=None)
    twitter_username = serializers.CharField(allow_null=True, default=None)
