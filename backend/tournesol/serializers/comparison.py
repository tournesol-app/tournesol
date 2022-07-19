from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from tournesol.models import Comparison, ComparisonCriteriaScore, Entity
from tournesol.serializers.entity import RelatedEntitySerializer


class ComparisonCriteriaScoreSerializer(ModelSerializer):
    class Meta:
        model = ComparisonCriteriaScore
        fields = ["criteria", "score", "weight"]

    def validate_criteria(self, value):
        current_poll = self.context["poll"]
        if value not in current_poll.criterias_list:
            raise ValidationError(
                f"'{value}' is not a valid criteria for poll '{current_poll.name}'"
            )
        return value


class ComparisonSerializerMixin:
    def reverse_criteria_scores(self, criteria_scores):
        opposite_scores = criteria_scores.copy()
        for index, score in enumerate(criteria_scores):
            opposite_scores[index]["score"] = score["score"] * -1

        return opposite_scores

    def validate_criteria_scores(self, value):
        current_poll = self.context["poll"]
        missing_criterias = set(current_poll.required_criterias_list) - set(
            score["criteria"] for score in value
        )
        if missing_criterias:
            raise ValidationError(
                f"Missing required criteria: {','.join(missing_criterias)}"
            )
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
    criteria_scores = ComparisonCriteriaScoreSerializer(many=True)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Comparison
        fields = ["user", "entity_a", "entity_b", "criteria_scores", "duration_ms"]

    def to_representation(self, instance):
        """
        Display the opposite of each criteria scores if the comparison is
        requested in the reverse order.
        """
        ret = super().to_representation(instance)

        if self.context.get("reverse", False):
            ret["entity_a"], ret["entity_b"] = ret["entity_b"], ret["entity_a"]
            ret["criteria_scores"] = self.reverse_criteria_scores(
                ret["criteria_scores"]
            )

        return ret

    @transaction.atomic
    def create(self, validated_data):
        uid_1 = validated_data.pop("entity_1").get("uid")
        uid_2 = validated_data.pop("entity_2").get("uid")
        # The validation performed by the `RelatedEntitySerializer` guarantees
        # that the submitted UIDs exist in the database.
        entity_1 = Entity.objects.get(uid=uid_1)
        entity_2 = Entity.objects.get(uid=uid_2)
        criteria_scores = validated_data.pop("criteria_scores")

        comparison = Comparison.objects.create(
            poll=self.context.get("poll"),
            entity_1=entity_1,
            entity_2=entity_2,
            **validated_data,
        )

        for criteria_score in criteria_scores:
            ComparisonCriteriaScore.objects.create(
                comparison=comparison, **criteria_score
            )

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

    class Meta:
        model = Comparison
        fields = ["criteria_scores", "duration_ms", "entity_a", "entity_b"]

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
            ret["criteria_scores"] = self.reverse_criteria_scores(
                ret["criteria_scores"]
            )

        ret.move_to_end("entity_b", last=False)
        ret.move_to_end("entity_a", last=False)
        return ret

    def to_internal_value(self, data):
        """
        Save the comparison in the order expected by the model, even if the
        comparison is provided reversed.
        """
        ret = super().to_internal_value(data)

        if self.context.get("reverse", False):
            ret["criteria_scores"] = self.reverse_criteria_scores(
                ret["criteria_scores"]
            )
        return ret

    @transaction.atomic
    def update(self, instance, validated_data):
        if validated_data.get("duration_ms"):
            instance.duration_ms = validated_data.get("duration_ms")

        instance.save()
        instance.criteria_scores.all().delete()

        for criteria_score in validated_data.pop("criteria_scores"):
            instance.criteria_scores.create(**criteria_score)

        return instance
