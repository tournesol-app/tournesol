from django.db import IntegrityError, transaction
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from tournesol.errors import ConflictError
from tournesol.models import RateLater
from tournesol.serializers.entity import RelatedEntitySerializer
from tournesol.serializers.entity_context import EntityContextSerializer
from tournesol.serializers.poll import CollectiveRatingSerializer, IndividualRatingSerializer


class RateLaterMetadataSerializer(ModelSerializer):
    class Meta:
        model = RateLater
        fields = ["created_at"]


class RateLaterListSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        result = []
        for attrs in validated_data:
            try:
                with transaction.atomic():
                    result.append(self.child.create(attrs))
            except ConflictError:
                # Ignore conflicts in bulk create
                pass

        return result


class RateLaterSerializer(ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    entity = RelatedEntitySerializer()
    entity_contexts = EntityContextSerializer(
        source="entity.single_poll_entity_contexts",
        read_only=True,
        many=True
    )
    collective_rating = CollectiveRatingSerializer(
        source="entity.single_poll_rating",
        read_only=True,
        allow_null=True,
    )
    individual_rating = IndividualRatingSerializer(
        source="entity.single_contributor_rating",
        read_only=True,
        allow_null=True,
    )
    rate_later_metadata = RateLaterMetadataSerializer(source="*", read_only=True)

    class Meta:
        model = RateLater
        fields = [
            "user",
            "entity",
            "collective_rating",
            "individual_rating",
            "entity_contexts",
            "rate_later_metadata",
        ]
        list_serializer_class = RateLaterListSerializer

    def create(self, validated_data):
        entity_id = validated_data.pop("entity")["pk"]
        try:
            rate_later = RateLater.objects.create(
                poll=self.context.get("poll"),
                entity_id=entity_id,
                **validated_data,
            )
        except IntegrityError as error:
            raise ConflictError(
                _("The entity is already in the rate-later list of this poll.")
            ) from error

        return rate_later
