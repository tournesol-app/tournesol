from rest_framework.serializers import ModelSerializer

from tournesol.models import ContributorRating, ContributorRatingCriteriaScore
from tournesol.serializers.poll import RecommendationSerializer


class ContributorRecommendationsScore(ModelSerializer):
    """ Outputs the recommending contributor's criteria scores for the given entity """
    class Meta:
        model = ContributorRatingCriteriaScore
        fields = ["criteria", "score"]


class ContributorRecommendationsRating(ModelSerializer):
    criteria_scores = ContributorRecommendationsScore(many=True)

    class Meta:
        model = ContributorRating
        fields = ["is_public", "criteria_scores"]


class ContributorRecommendationsSerializer(RecommendationSerializer):
    """ Format the output of the contributor_recommendations views """
    contributor_ratings = ContributorRecommendationsRating(many=True,
                                                           source="contributorvideoratings")

    class Meta(RecommendationSerializer.Meta):
        fields = list((set(RecommendationSerializer.Meta.fields)
                      - {"criteria_scores"}) | {"contributor_ratings"})
