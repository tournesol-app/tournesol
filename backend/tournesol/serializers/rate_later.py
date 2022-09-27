from django.db import IntegrityError
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from tournesol.errors import ConflictError
from tournesol.models import Entity, RateLater
from tournesol.serializers.entity import RelatedEntitySerializer


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
        except IntegrityError as error:
            raise ConflictError(
                _("The entity is already in the rate-later list of this poll.")
            ) from error

        return rate_later
