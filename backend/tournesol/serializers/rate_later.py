from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.serializers import Serializer

from tournesol.errors import ConflictError
from tournesol.models import Entity, RateLater
from tournesol.serializers.entity import RelatedVideoSerializer


class RateLaterLegacySerializer(Serializer):
    """
    A serializer transporting `RateLater` data using the legacy couple user
    and video.

    The poll is automatically set to the default poll by the `RateLater`
    model.
    """

    video = RelatedVideoSerializer()
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = RateLater
        fields = ["user", "video"]

    def create(self, validated_data):
        video_id = validated_data.pop("video")["video_id"]
        video = Entity.get_from_video_id(video_id)

        try:
            return RateLater.objects.create(entity=video, **validated_data)
        except IntegrityError:
            raise ConflictError

    def to_representation(self, instance):
        # From Entity to legacy Video
        return {
            "video": {
                "uid": instance.entity.uid,
                "name": instance.entity.metadata.get("name"),
                "description": instance.entity.metadata.get("description"),
                "publication_date": instance.entity.metadata.get("publication_date"),
                "views": instance.entity.metadata.get("views"),
                "uploader": instance.entity.metadata.get("uploader"),
                "language": instance.entity.metadata.get("language"),
                "duration": instance.entity.metadata.get("duration"),
                "video_id": instance.entity.metadata["video_id"],
            }
        }
