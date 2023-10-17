from rest_framework import serializers

from tournesol.serializers.entity import RelatedEntitySerializer
from tournesol.serializers.poll import CollectiveRatingSerializer


class ResultFromPollRating(serializers.Serializer):
    entity = RelatedEntitySerializer()
    collective_rating = CollectiveRatingSerializer(
        source="*",
        read_only=True,
    )


class ResultFromRelatedEntity(serializers.Serializer):
    entity = RelatedEntitySerializer()
    collective_rating = CollectiveRatingSerializer(
        source="entity.single_poll_rating",
        read_only=True,
    )
