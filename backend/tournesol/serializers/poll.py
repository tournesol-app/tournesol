from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers
from rest_framework.serializers import IntegerField, ModelSerializer

from tournesol.models import ContributorRating, CriteriaRank, Entity, EntityPollRating, Poll
from tournesol.models.entity_poll_rating import UNSAFE_REASONS
from tournesol.serializers.entity import EntityCriteriaScoreSerializer, RelatedEntitySerializer


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


class RecommendationMetadataSerializer(serializers.Serializer):
    total_score = serializers.FloatField(read_only=True, allow_null=True)


@extend_schema_serializer(
    exclude_fields=[
        # legacy fields have been moved to "entity", "collective_rating", etc.
        "uid",
        "type",
        "n_comparisons",
        "n_contributors",
        "metadata",
        "total_score",
        "tournesol_score",
        "criteria_scores",
        "unsafe",
    ]
)
class RecommendationSerializer(ModelSerializer):
    # pylint: disable=duplicate-code
    n_comparisons = serializers.IntegerField(source="rating_n_ratings")
    n_contributors = serializers.IntegerField(source="rating_n_contributors")
    criteria_scores = EntityCriteriaScoreSerializer(many=True)
    # TODO: the field total_score is the only field in this serializer that
    # on the parameters of an api request. Should it be treated differently?
    total_score = serializers.FloatField()
    unsafe = UnsafeStatusSerializer(
        source="single_poll_rating", allow_null=True, default=None, read_only=True
    )

    entity = RelatedEntitySerializer(source="*", read_only=True)
    collective_rating = ExtendedCollectiveRatingSerializer(
        source="single_poll_rating",
        read_only=True,
        allow_null=True,
    )
    recommendation_metadata = RecommendationMetadataSerializer(source="*", read_only=True)

    class Meta:
        model = Entity
        fields = [
            "uid",
            "type",
            "n_comparisons",
            "n_contributors",
            "metadata",
            "total_score",
            "tournesol_score",
            "criteria_scores",
            "unsafe",
            "entity",
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
