"""
Serializers of the `backoffice` app.
"""
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from backoffice.models import TalkEntry


class TalkEntrySerializer(ModelSerializer):

    date_gmt = serializers.CharField(source="get_date_gmt")

    class Meta:
        model = TalkEntry
        fields = ["name", "title", "abstract", "invitation_link", "youtube_link", "speakers",
                  "date", "date_gmt"]
