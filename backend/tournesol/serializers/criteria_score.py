from rest_framework.serializers import ModelSerializer

from tournesol.models import ContributorRatingCriteriaScore


class ContributorCriteriaScoreSerializer(ModelSerializer):
    class Meta:
        model = ContributorRatingCriteriaScore
        fields = ["criteria", "score", "uncertainty"]
