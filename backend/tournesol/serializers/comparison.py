from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from tournesol.models import Comparison, ComparisonCriteriaScore, Entity
from tournesol.serializers.entity import RelatedVideoSerializer, VideoSerializer


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


class ComparisonSerializer(ComparisonSerializerMixin, ModelSerializer):
    """
    A comparison serializer used for the operations create, retrieve and list.

    Given the context determined by the view, it will represent the comparison
    in the reverse order.

    Use `ComparisonUpdateSerializer` for the update operation.
    """

    entity_a = RelatedVideoSerializer(source="entity_1")
    entity_b = RelatedVideoSerializer(source="entity_2")
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
        ret = super(ComparisonSerializer, self).to_representation(instance)

        if self.context.get("reverse", False):
            ret["entity_a"], ret["entity_b"] = ret["entity_b"], ret["entity_a"]
            ret["criteria_scores"] = self.reverse_criteria_scores(
                ret["criteria_scores"]
            )

        return ret

    @transaction.atomic
    def create(self, validated_data):
        video_id_1 = validated_data.pop("entity_1").get("video_id")
        video_id_2 = validated_data.pop("entity_2").get("video_id")
        # the validation performed by the RelatedVideoSerializer guarantees
        # that the videos submitted exist in the database
        video_1 = Entity.objects.get(video_id=video_id_1)
        video_2 = Entity.objects.get(video_id=video_id_2)
        criteria_scores = validated_data.pop("criteria_scores")

        comparison = Comparison.objects.create(
            poll=self.context.get("poll"),
            entity_1=video_1,
            entity_2=video_2,
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
    entity_a = VideoSerializer(source="entity_1", read_only=True)
    entity_b = VideoSerializer(source="entity_2", read_only=True)

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
        ret = super(ComparisonUpdateSerializer, self).to_representation(instance)

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
        ret = super(ComparisonUpdateSerializer, self).to_internal_value(data)

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
