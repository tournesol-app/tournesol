from drf_spectacular.utils import extend_schema_field
from rest_framework.serializers import SerializerMethodField

from tournesol.serializers.poll import RecommendationSerializer
from tournesol.serializers.rating import ContributorCriteriaScore


class ContributorRecommendationsSerializer(RecommendationSerializer):
    """
    An entity recommended by a user.

    In addition to the fields inherited from `RecommendationSerializer`, this
    serializer also display the public status of the `ContributorRating`
    related to the trio poll / entity / user.

    Note that the fields `n_comparisons` and `n_contributors` contain
    the collective values, and are not specific to the user.
    """
    is_public = SerializerMethodField()
    criteria_scores = SerializerMethodField()

    class Meta(RecommendationSerializer.Meta):
        fields = list(
            set(RecommendationSerializer.Meta.fields)
            | {"is_public"}
        )

    @extend_schema_field(ContributorCriteriaScore(many=True))
    def get_criteria_scores(self, obj):
        return ContributorCriteriaScore(
            obj.contributorvideoratings.all()[0].criteria_scores.all(), many=True
        ).data

    def get_is_public(self, obj) -> bool:
        return obj.contributorvideoratings.all()[0].is_public
