from rest_framework import serializers

from backoffice.banner.models import Banner
from backoffice.talk.models import TalkEntry


class TalkEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = TalkEntry
        fields = [
            "name",
            "title",
            "date",
            "date_as_tz_europe_paris",
            "speakers",
            "abstract",
            "invitation_link",
            "youtube_link",
        ]


class BannerSerializer(serializers.ModelSerializer):
    text = serializers.CharField(source="get_content_prefetch")
    title = serializers.CharField(source="get_title_prefetch")

    class Meta:
        model = Banner
        fields = [
            "name",
            "text",
            "title",
            "get_text",
            "date_start",
            "date_end",
            "security_advisory",
        ]
