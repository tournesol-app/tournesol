from rest_framework import serializers

from backoffice.models import TalkEntry


class TournesolEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = TalkEntry
        fields = [
            "name",
            "title",
            "event_type",
            "date",
            "date_as_tz_europe_paris",
            "speakers",
            "abstract",
            "invitation_link",
            "youtube_link",
        ]
