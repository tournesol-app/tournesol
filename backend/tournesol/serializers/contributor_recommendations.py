from tournesol.models.ratings import ContributorRating
from tournesol.serializers.criteria_score import ContributorCriteriaScoreSerializer
from tournesol.serializers.poll import IndividualRatingSerializer, RecommendationSerializer


class IndividualRatingWithScoresSerializer(IndividualRatingSerializer):
    criteria_scores = ContributorCriteriaScoreSerializer(many=True, read_only=True)

    class Meta:
        model = ContributorRating
        fields = IndividualRatingSerializer.Meta.fields + ["criteria_scores"]
        read_only_fields = fields


class ContributorRecommendationsSerializer(RecommendationSerializer):
    """
    An entity recommended by a user.
    """
    individual_rating = IndividualRatingWithScoresSerializer(
        source="single_contributor_rating",
        read_only=True,
    )

    class Meta(RecommendationSerializer.Meta):
        fields = RecommendationSerializer.Meta.fields + ["individual_rating"]
