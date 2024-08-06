from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from tournesol.models import Comparison, ComparisonCriteriaScore
from tournesol.serializers.entity import RelatedEntitySerializer
from tournesol.serializers.entity_context import EntityContextSerializer


class ComparisonCriteriaScoreSerializer(ModelSerializer):
    class Meta:
        model = ComparisonCriteriaScore
        fields = ["criteria", "score", "score_max", "weight"]

    def validate_criteria(self, value):
        current_poll = self.context["poll"]
        if value not in current_poll.criterias_list:
            raise ValidationError(
                f"'{value}' is not a valid criteria for poll '{current_poll.name}'"
            )
        return value

    def validate(self, attrs):
        try:
            ComparisonCriteriaScore.validate_score_max(
                attrs["score"],
                attrs["score_max"],
                attrs["criteria"],
            )
        except (TypeError, ValueError) as err:
            raise ValidationError({"score_max": err.args[0]}) from err
        return attrs


class ComparisonSerializerMixin:
    def format_entity_contexts(self, poll, contexts, metadata):
        return EntityContextSerializer(
            poll.get_entity_contexts(metadata, contexts), many=True
        ).data

    def reverse_criteria_scores(self, criteria_scores):
        opposite_scores = criteria_scores.copy()
        for index, score in enumerate(criteria_scores):
            opposite_scores[index]["score"] = score["score"] * -1

        return opposite_scores

    def validate_criteria_scores(self, value):
        current_poll = self.context["poll"]
        partial_update = self.context.get("partial_update")

        if not partial_update:
            missing_criterias = set(current_poll.required_criterias_list) - set(
                score["criteria"] for score in value
            )
            if missing_criterias:
                raise ValidationError(f"Missing required criteria: {','.join(missing_criterias)}")

        return value


class ComparisonSerializer(ComparisonSerializerMixin, ModelSerializer):
    """
    A comparison serializer used for the operations create, retrieve and list.

    Given the context determined by the view, it will represent the comparison
    in the reverse order.

    Use `ComparisonUpdateSerializer` for the update operation.
    """

    entity_a = RelatedEntitySerializer(source="entity_1")
    entity_b = RelatedEntitySerializer(source="entity_2")
    entity_a_contexts = EntityContextSerializer(read_only=True, many=True, default=[])
    entity_b_contexts = EntityContextSerializer(read_only=True, many=True, default=[])

    criteria_scores = ComparisonCriteriaScoreSerializer(many=True)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Comparison
        fields = [
            "user",
            "entity_a",
            "entity_b",
            "entity_a_contexts",
            "entity_b_contexts",
            "criteria_scores",
            "duration_ms",
        ]

    def to_representation(self, instance):
        """
        Display the opposite of each criteria scores if the comparison is
        requested in the reverse order.
        """
        ret = super().to_representation(instance)

        if self.context.get("reverse", False):
            ret["entity_a"], ret["entity_b"] = ret["entity_b"], ret["entity_a"]
            ret["criteria_scores"] = self.reverse_criteria_scores(ret["criteria_scores"])

        poll = self.context.get("poll")
        ent_contexts = self.context.get("entity_contexts")

        if poll is not None and ent_contexts is not None:
            ret["entity_a_contexts"] = self.format_entity_contexts(
                poll, ent_contexts, ret["entity_a"]["metadata"]
            )
            ret["entity_b_contexts"] = self.format_entity_contexts(
                poll, ent_contexts, ret["entity_b"]["metadata"]
            )

        return ret

    @transaction.atomic
    def create(self, validated_data):
        # The validation performed by the `RelatedEntitySerializer` guarantees
        # that the submitted UIDs exist in the database.
        entity_1_id = validated_data.pop("entity_1")["pk"]
        entity_2_id = validated_data.pop("entity_2")["pk"]
        criteria_scores = validated_data.pop("criteria_scores")

        comparison = Comparison.objects.create(
            poll=self.context.get("poll"),
            entity_1_id=entity_1_id,
            entity_2_id=entity_2_id,
            **validated_data,
        )

        for criteria_score in criteria_scores:
            ComparisonCriteriaScore.objects.create(comparison=comparison, **criteria_score)

        return comparison


class ComparisonUpdateSerializer(ComparisonSerializerMixin, ModelSerializer):
    """
    A comparison serializer used only for updates.

    Given the context determined by the view, it will represent or save the
    comparison in the reverse order.

    Use `ComparisonSerializer` for all other operations.
    """

    criteria_scores = ComparisonCriteriaScoreSerializer(many=True)
    entity_a = RelatedEntitySerializer(source="entity_1", read_only=True)
    entity_b = RelatedEntitySerializer(source="entity_2", read_only=True)
    entity_a_contexts = EntityContextSerializer(read_only=True, many=True, default=[])
    entity_b_contexts = EntityContextSerializer(read_only=True, many=True, default=[])

    class Meta:
        model = Comparison
        fields = [
            "criteria_scores",
            "duration_ms",
            "entity_a",
            "entity_b",
            "entity_a_contexts",
            "entity_b_contexts",
        ]

    def to_representation(self, instance):
        """
        Display the opposite of each criteria scores if the comparison is
        requested in the reverse order.

        Also add `entity_a` and `entity_b` fields to make the representation
        consistent across all comparison serializers.
        """
        ret = super().to_representation(instance)

        if self.context.get("reverse", False):
            ret["entity_a"], ret["entity_b"] = ret["entity_b"], ret["entity_a"]
            ret["criteria_scores"] = self.reverse_criteria_scores(ret["criteria_scores"])

        poll = self.context.get("poll")
        ent_contexts = self.context.get("entity_contexts")

        if poll is not None and ent_contexts is not None:
            ret["entity_a_contexts"] = self.format_entity_contexts(
                poll, ent_contexts, ret["entity_a"]["metadata"]
            )
            ret["entity_b_contexts"] = self.format_entity_contexts(
                poll, ent_contexts, ret["entity_b"]["metadata"]
            )

        return ret

    def to_internal_value(self, data):
        """
        Save the comparison in the order expected by the model, even if the
        comparison is provided reversed.
        """
        ret = super().to_internal_value(data)

        if self.context.get("reverse", False):
            ret["criteria_scores"] = self.reverse_criteria_scores(ret["criteria_scores"])
        return ret

    @transaction.atomic
    def update(self, instance, validated_data):
        if validated_data.get("duration_ms"):
            instance.duration_ms = validated_data.get("duration_ms")

        instance.save()

        partial_update = self.context.get("partial_update")

        if partial_update:
            for criteria_score in validated_data.pop("criteria_scores"):
                instance.criteria_scores.update_or_create(
                    criteria=criteria_score["criteria"],
                    defaults={**criteria_score}
                )
        else:
            instance.criteria_scores.all().delete()

            for criteria_score in validated_data.pop("criteria_scores"):
                instance.criteria_scores.create(**criteria_score)

        return instance
