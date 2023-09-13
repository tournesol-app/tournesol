from rest_framework import serializers

from tournesol.serializers.entity import RelatedEntitySerializer


class SubSampleSerializer(serializers.Serializer):
    entity = RelatedEntitySerializer()

    class Meta:
        fields = [
            "entity",
        ]
