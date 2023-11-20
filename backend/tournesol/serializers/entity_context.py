from rest_framework import serializers

from tournesol.models.entity_context import EntityContext


class EntityContextSerializer(serializers.ModelSerializer):
    text = serializers.CharField(source="get_context_text_prefetch")

    class Meta:
        model = EntityContext
        fields = ['origin', 'unsafe', 'text', 'created_at']
