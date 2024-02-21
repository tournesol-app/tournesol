from rest_framework import serializers

from tournesol.serializers.entity import EntityNoExtraFieldSerializer
from tournesol.serializers.entity_context import EntityContextSerializer


class UnconnectedEntitySerializer(serializers.Serializer):
    entity = EntityNoExtraFieldSerializer(source="*")
    entity_contexts = EntityContextSerializer(read_only=True, many=True, default=[])

    def to_representation(self, instance):
        ret = super().to_representation(instance)

        poll = self.context["poll"]
        ent_contexts = self.context.get("entity_contexts")

        if ent_contexts is not None:
            ret["entity_contexts"] = EntityContextSerializer(
                poll.get_entity_contexts(ret["entity"]["metadata"], ent_contexts), many=True
            ).data

        return ret
