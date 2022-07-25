from django.db import IntegrityError
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, Serializer

from tournesol.errors import ConflictError
from tournesol.models import Entity, RateLater
from tournesol.serializers.entity import RelatedEntitySerializer, RelatedVideoSerializer


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
            return RateLater.objects.create(
                entity=video, poll=self.context.get("poll"), **validated_data
            )
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
                # The two following fields will be moved in related tables.
                "rating_n_ratings": instance.entity.rating_n_ratings,
                "rating_n_contributors": instance.entity.rating_n_contributors,
                "duration": instance.entity.metadata.get("duration"),
                "video_id": instance.entity.metadata["video_id"],
            }
        }


class RateLaterSerializer(ModelSerializer):
    entity = RelatedEntitySerializer(True)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = RateLater
        fields = ["entity", "user", "created_at"]

    def create(self, validated_data):
        uid = validated_data.pop("entity").get("uid")
        entity = Entity.objects.get(uid=uid)

        try:
            rate_later = RateLater.objects.create(
                poll=self.context.get("poll"),
                entity=entity,
                **validated_data,
            )
        except IntegrityError:
            raise ConflictError(
                _("The entity is already in the rate-later list of this poll.")
            )

        return rate_later
