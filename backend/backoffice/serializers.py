from rest_framework.serializers import ModelSerializer

from backoffice.banner.models import Banner
from backoffice.talk.models import TalkEntry


class TalkEntrySerializer(ModelSerializer):
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


class BannerSerializer(ModelSerializer):
    class Meta:
        model = Banner
        fields = [
            "name",
            "text",
            "date_start",
            "date_end",
            "security_advisory",
        ]
