from rest_framework.serializers import ModelSerializer

from backoffice.models import TalkEntry


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
