from drf_spectacular.utils import extend_schema_field
from rest_framework.serializers import SerializerMethodField

from tournesol.serializers.poll import RecommendationSerializer
from tournesol.serializers.rating import ContributorCriteriaScore


class ContributorRecommendationsSerializer(RecommendationSerializer):
    is_public = SerializerMethodField()
    criteria_scores = SerializerMethodField()

    class Meta(RecommendationSerializer.Meta):
        fields = RecommendationSerializer.Meta.fields + ["is_public"]

    @extend_schema_field(ContributorCriteriaScore(many=True))
    def get_criteria_scores(self, obj):
        return ContributorCriteriaScore(
            obj.contributorvideoratings.first().criteria_scores.all(), many=True
        ).data

    def get_is_public(self, obj) -> bool:
        return obj.contributorvideoratings.first().is_public
