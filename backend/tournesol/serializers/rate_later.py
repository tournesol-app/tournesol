from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from tournesol.errors import ConflictError
from tournesol.models import Entity, RateLater
from tournesol.serializers.entity import RelatedEntitySerializer


class RateLaterSerializer(ModelSerializer):
    entity = RelatedEntitySerializer()
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = RateLater
        fields = ["user", "entity"]

    def create(self, validated_data):
        uid = validated_data.pop("entity")["uid"]
        entity = Entity.objects.get(uid=uid)
        poll = self.context["poll"]
        try:
            return super().create({"entity": entity, "poll": poll, **validated_data})
        except IntegrityError:
            raise ConflictError
