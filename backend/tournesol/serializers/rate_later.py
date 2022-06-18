from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from tournesol.errors import ConflictError
from tournesol.models import Entity, Poll, RateLater
from tournesol.serializers.entity import EntityNoExtraFieldSerializer
from tournesol.serializers.poll import PollSerializer


class RateLaterSerializer(ModelSerializer):
    entity = EntityNoExtraFieldSerializer(read_only=True)
    poll = PollSerializer(read_only=True)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = RateLater
        fields = ["user", "entity", "poll"]
        read_only_fields = ["entity", "poll"]

    def create(self, validated_data):
        video_id = validated_data.pop("video")["video_id"]
        entity = Entity.get_from_video_id(video_id)
        poll = Poll.default_poll()
        try:
            return super().create({"entity": entity, "poll": poll})
        except IntegrityError:
            raise ConflictError
