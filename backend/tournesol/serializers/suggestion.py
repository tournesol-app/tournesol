from rest_framework import serializers

from tournesol.serializers.entity import RelatedEntitySerializer
from tournesol.serializers.poll import CollectiveRatingSerializer


class EntityToCompare(serializers.Serializer):
    entity = RelatedEntitySerializer(source="*")
    collective_rating = CollectiveRatingSerializer(
        source="single_poll_rating",
        read_only=True,
    )
