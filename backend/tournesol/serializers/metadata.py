from rest_framework import serializers

from core.utils.constants import YOUTUBE_VIDEO_ID_REGEX


class VideoMetadata(serializers.Serializer):
    source = serializers.CharField(allow_blank=True, default="")
    video_id = serializers.RegexField(YOUTUBE_VIDEO_ID_REGEX)
    name = serializers.CharField(allow_blank=True, default="")
    description = serializers.CharField(allow_blank=True, default="")
    uploader = serializers.CharField(allow_blank=True, default="")
    channel_id = serializers.CharField(allow_null=True, default=None)
    publication_date = serializers.DateField(allow_null=True, default=None)
    duration = serializers.IntegerField(
        allow_null=True,
        default=None,
        help_text="Duration in seconds"
    )
    views = serializers.IntegerField(allow_null=True, default=None)
    language = serializers.CharField(allow_null=True, default=None)
    tags = serializers.ListField(child=serializers.CharField(), default=list)
    is_unlisted = serializers.BooleanField(default=False)
