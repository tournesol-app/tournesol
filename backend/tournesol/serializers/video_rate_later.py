from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from tournesol.errors import ConflictError
from tournesol.models import Entity, VideoRateLater
from tournesol.serializers.entity import RelatedVideoSerializer


class VideoRateLaterSerializer(ModelSerializer):
    video = RelatedVideoSerializer()
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = VideoRateLater
        fields = ["user", "video"]

    def create(self, validated_data):
        video_id = validated_data.pop("video")["video_id"]
        video = Entity.objects.get(video_id=video_id)
        try:
            return super().create({"video": video, **validated_data})
        except IntegrityError:
            raise ConflictError
