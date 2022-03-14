from rest_framework.serializers import ModelSerializer

from tournesol.models import ContributorRating
from tournesol.serializers.poll import RecommendationSerializer
from tournesol.serializers.rating import ContributorCriteriaScore


class ContributorRecommendationsRatingsSerializer(ModelSerializer):
    criteria_scores = ContributorCriteriaScore(many=True)

    class Meta:
        model = ContributorRating
        fields = ["is_public", "criteria_scores"]


class ContributorRecommendationsSerializer(RecommendationSerializer):
    contributor_ratings = ContributorRecommendationsRatingsSerializer(
        many=True, source="contributorvideoratings"
    )

    class Meta(RecommendationSerializer.Meta):
        fields = list(
            (set(RecommendationSerializer.Meta.fields) - {"criteria_scores"})
            | {"contributor_ratings"}
        )
