from rest_framework import serializers

from backoffice.models import Banner, TalkEntry


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
    title = serializers.CharField(source="get_title_prefetch")
    text = serializers.CharField(source="get_paragraph_prefetch")
    action_label = serializers.CharField(source="get_action_label_prefetch")
    action_link = serializers.CharField(source="get_action_link_prefetch")

    class Meta:
        model = Banner
        fields = [
            "name",
            "date_start",
            "date_end",
            "title",
            "text",
            "action_label",
            "action_link",
            "priority",
            "security_advisory",
        ]
