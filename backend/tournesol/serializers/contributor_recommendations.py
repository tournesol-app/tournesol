from drf_spectacular.utils import extend_schema_field
from rest_framework.serializers import SerializerMethodField

from tournesol.serializers.poll import RecommendationSerializer
from tournesol.serializers.rating import ContributorCriteriaScore


class ContributorRecommendationsSerializer(RecommendationSerializer):
    is_public = SerializerMethodField()
    criteria_scores = SerializerMethodField()

    class Meta(RecommendationSerializer.Meta):
        # By default, `n_comparisons` and `n_contributors` take all
        # contributors into account, so they are removed here to not add
        # confusion in the contributor recommendations. We could choose to
        # display the `n_comparisons` of the selected contributor by computing
        # it here.
        fields = list(
            set(RecommendationSerializer.Meta.fields)
            - {"n_comparisons"}
            - {"n_contributors"}
            | {"is_public"}
        )

    @extend_schema_field(ContributorCriteriaScore(many=True))
    def get_criteria_scores(self, obj):
        return ContributorCriteriaScore(
            obj.contributorvideoratings.all()[0].criteria_scores.all(), many=True
        ).data

    def get_is_public(self, obj) -> bool:
        return obj.contributorvideoratings.all()[0].is_public
