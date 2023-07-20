from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from tournesol.models import CriteriaRank, Entity, EntityPollRating, Poll
from tournesol.serializers.entity import EntityCriteriaScoreSerializer


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
        child=serializers.CharField(), source="unsafe_recommendation_reasons"
    )

    class Meta:
        model = EntityPollRating
        fields = [
            "status",
            "reasons",
        ]


class RecommendationSerializer(ModelSerializer):
    n_comparisons = serializers.IntegerField(source="rating_n_ratings")
    n_contributors = serializers.IntegerField(source="rating_n_contributors")
    criteria_scores = EntityCriteriaScoreSerializer(many=True)
    # TODO: the field total_score is the only field in this serializer that
    # on the parameters of an api request. Should it be treated differently?
    total_score = serializers.FloatField()
    unsafe = UnsafeStatusSerializer(source="single_poll_rating", allow_null=True, default=None)

    # pylint: disable=duplicate-code
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
        ]
        read_only_fields = [
            "metadata",
        ]


@extend_schema_serializer(
    # TODO: include this parameter in schema + docs, after the cache behavior is fixed.
    exclude_fields=["exclude_compared_entities"],
)
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
