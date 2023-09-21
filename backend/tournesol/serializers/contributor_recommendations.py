from drf_spectacular.utils import extend_schema_field, extend_schema_serializer
from rest_framework.serializers import SerializerMethodField

from tournesol.models.ratings import ContributorRating
from tournesol.serializers.criteria_score import ContributorCriteriaScoreSerializer
from tournesol.serializers.poll import IndividualRatingSerializer, RecommendationSerializer


class IndividualRatingWithScoresSerializer(IndividualRatingSerializer):
    criteria_scores = ContributorCriteriaScoreSerializer(many=True, read_only=True)

    class Meta:
        model = ContributorRating
        fields = IndividualRatingSerializer.Meta.fields + ["criteria_scores"]
        read_only_fields = fields


@extend_schema_serializer(
    deprecate_fields=[
        # legacy fields have been moved to "entity", "invidual_rating", "collective_rating", etc.
        "uid",
        "type",
        "n_comparisons",
        "n_contributors",
        "metadata",
        "total_score",
        "tournesol_score",
        "criteria_scores",
        "unsafe",
        "is_public",
    ]
)
class ContributorRecommendationsSerializer(RecommendationSerializer):
    """
    An entity recommended by a user.
    """

    is_public = SerializerMethodField()
    criteria_scores = SerializerMethodField()
    individual_rating = IndividualRatingWithScoresSerializer(
        source="single_contributor_rating",
        read_only=True,
    )

    class Meta(RecommendationSerializer.Meta):
        fields = RecommendationSerializer.Meta.fields + ["is_public", "individual_rating"]

    @extend_schema_field(ContributorCriteriaScoreSerializer(many=True))
    def get_criteria_scores(self, obj):
        return ContributorCriteriaScoreSerializer(
            obj.contributorvideoratings.all()[0].criteria_scores.all(), many=True
        ).data

    def get_is_public(self, obj) -> bool:
        return obj.contributorvideoratings.all()[0].is_public
