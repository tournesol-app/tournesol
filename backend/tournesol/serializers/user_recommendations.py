from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from tournesol.models import ContributorRating, ContributorRatingCriteriaScore, Entity


class UserRecommendationsScore(ModelSerializer):
    """ Outputs the recommending user's criteria scores for the given entity """
    class Meta:
        model = ContributorRatingCriteriaScore
        fields = ["criteria", "score"]


class UserRecommendationsRating(ModelSerializer):
    criteria_scores = UserRecommendationsScore(many=True)

    class Meta:
        model = ContributorRating
        fields = ["criteria_scores"]


class UserRecommendationsSerializer(ModelSerializer):
    """ Format the output of user_recommendations views """
    n_comparisons = serializers.IntegerField(source="rating_n_ratings")
    n_contributors = serializers.IntegerField(source="rating_n_contributors")
    total_score = serializers.FloatField()
    contributorvideoratings = UserRecommendationsRating(many=True)

    class Meta:
        model = Entity
        fields = [
            "uid",
            "metadata",
            "n_comparisons",
            "n_contributors",
            "total_score",
            "contributorvideoratings",
        ]
