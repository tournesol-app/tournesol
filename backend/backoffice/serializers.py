"""
Serializers of the `backoffice` app.
"""
import pytz
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from backoffice.models import TalkEntry


class TalkEntrySerializer(ModelSerializer):

    date_gmt = serializers.DateTimeField(source="date",
                                         default_timezone=pytz.timezone("Europe/Paris"))

    class Meta:
        model = TalkEntry
        fields = ["name", "title", "abstract", "invitation_link", "youtube_link", "speaker",
                  "speaker_short_desc", "date", "date_gmt"]
