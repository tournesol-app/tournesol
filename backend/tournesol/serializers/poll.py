from rest_framework import serializers
from rest_framework.serializers import IntegerField, ModelSerializer

from tournesol.models import ContributorRating, CriteriaRank, EntityPollRating, Poll
from tournesol.models.entity_poll_rating import UNSAFE_REASONS
from tournesol.serializers.entity import EntityCriteriaScoreSerializer, RelatedEntitySerializer
from tournesol.serializers.entity_context import EntityContextSerializer


class PollCriteriaSerializer(ModelSerializer):
    name = serializers.CharField(source="criteria.name")
    label = serializers.CharField(source="criteria.get_label")

    class Meta:
        model = CriteriaRank
        fields = ["name", "label", "optional"]


class PollSerializer(ModelSerializer):
    criterias = PollCriteriaSerializer(source="criteriarank_set", many=True)

    class Meta:
        model = Poll
        fields = ["name", "criterias", "entity_type", "active"]


class UnsafeStatusSerializer(ModelSerializer):
    status = serializers.BooleanField(source="is_recommendation_unsafe")
    reasons = serializers.ListField(
        child=serializers.ChoiceField(choices=UNSAFE_REASONS),
        source="unsafe_recommendation_reasons",
    )

    class Meta:
        model = EntityPollRating
        fields = [
            "status",
            "reasons",
        ]


class CollectiveRatingSerializer(ModelSerializer):
    unsafe = UnsafeStatusSerializer(source="*", read_only=True)

    class Meta:
        model = EntityPollRating
        fields = [
            "n_comparisons",
            "n_contributors",
            "tournesol_score",
            "unsafe",
        ]
        read_only_fields = fields


class ExtendedCollectiveRatingSerializer(CollectiveRatingSerializer):
    criteria_scores = EntityCriteriaScoreSerializer(source="entity.criteria_scores", many=True)

    class Meta:
        model = CollectiveRatingSerializer.Meta.model
        fields = CollectiveRatingSerializer.Meta.fields + ["criteria_scores"]
        read_only_fields = fields


class IndividualRatingSerializer(ModelSerializer):
    n_comparisons = IntegerField(read_only=True, default=0)

    class Meta:
        model = ContributorRating
        fields = [
            "is_public",
            "n_comparisons",
        ]
        read_only_fields = fields


class RecommendationBaseSerializer(serializers.Serializer):
    """
    A base serializer for all recommendations.

    The recommendations of a poll should always be provided with
    the fields defined in this serializer.
    """
    entity = RelatedEntitySerializer(source="*", read_only=True)
    entity_contexts = EntityContextSerializer(
        source="single_poll_entity_contexts",
        read_only=True,
        many=True
    )
    collective_rating = ExtendedCollectiveRatingSerializer(
        source="single_poll_rating",
        read_only=True,
        allow_null=True,
    )

    class Meta:
        fields = [
            "entity",
            "entity_contexts",
            "collective_rating",
        ]
        read_only_fields = fields


class RecommendationMetadataSerializer(serializers.Serializer):
    total_score = serializers.FloatField(read_only=True, allow_null=True)


class RecommendationSerializer(RecommendationBaseSerializer):
    """
    An entity recommended in a poll.
    """
    recommendation_metadata = RecommendationMetadataSerializer(source="*", read_only=True)

    class Meta:
        fields = [
            "entity",
            "entity_contexts",
            "collective_rating",
            "recommendation_metadata",
        ]
        read_only_fields = fields


class RecommendationsFilterSerializer(serializers.Serializer):
    date_lte = serializers.DateTimeField(default=None)
    date_gte = serializers.DateTimeField(default=None)
    search = serializers.CharField(default=None, help_text="A search query to filter entities")
    unsafe = serializers.BooleanField(
        default=False,
        help_text="If true, entities considered as unsafe recommendations because of a"
        " low score or due to too few contributions will be included.",
    )
    exclude_compared_entities = serializers.BooleanField(
        default=False,
        help_text="If true and a user is authenticated, then entities compared by the"
        " user will be removed from the response",
    )


class RecommendationsRandomFilterSerializer(serializers.Serializer):
    bundle = serializers.IntegerField(
        default=None,
        help_text="Successive calls can return the same cached results. Vary"
        " this parameter to request new results."
    )
    date_lte = serializers.DateTimeField(default=None)
    date_gte = serializers.DateTimeField(default=None)
