from rest_framework import serializers
from rest_framework.fields import IntegerField

from tournesol.serializers.entity import RelatedEntitySerializer
from tournesol.serializers.entity_context import EntityContextSerializer
from tournesol.serializers.poll import CollectiveRatingSerializer
from tournesol.serializers.rating import ExtendedInvididualRatingSerializer


class SubSampleMetadataSerializer(serializers.Serializer):
    bucket = IntegerField(read_only=True)


class SubSampleSerializer(serializers.Serializer):
    entity = RelatedEntitySerializer()
    entity_contexts = EntityContextSerializer(
        source="entity.single_poll_entity_contexts", read_only=True, many=True, default=[]
    )

    individual_rating = ExtendedInvididualRatingSerializer(source="*", read_only=True)
    collective_rating = CollectiveRatingSerializer(
        source="entity.single_poll_rating",
        read_only=True,
    )

    subsample_metadata = SubSampleMetadataSerializer(source="*", read_only=True)
