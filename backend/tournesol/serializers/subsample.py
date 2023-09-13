from rest_framework import serializers

from tournesol.serializers.entity import RelatedEntitySerializer
from tournesol.serializers.poll import CollectiveRatingSerializer
from tournesol.serializers.rating import ExtendedInvididualRatingSerializer


class SubSampleSerializer(serializers.Serializer):
    entity = RelatedEntitySerializer()
    individual_rating = ExtendedInvididualRatingSerializer(source="*")
    collective_rating = CollectiveRatingSerializer(
        source="entity.single_poll_rating",
    )
