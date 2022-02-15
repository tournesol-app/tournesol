from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from tournesol.models import CriteriaRank, Entity, Poll
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
        fields = ["name", "criterias"]


class RecommendationSerializer(ModelSerializer):
    n_comparisons = serializers.IntegerField(source="rating_n_ratings")
    n_contributors = serializers.IntegerField(source="rating_n_contributors")
    criteria_scores = EntityCriteriaScoreSerializer(many=True)
    total_score = serializers.FloatField()

    class Meta:
        model = Entity
        fields = [
            "uid",
            "n_comparisons",
            "n_contributors",
            "metadata",
            "total_score",
            "criteria_scores",
        ]


class RecommendationsFilterSerializer(serializers.Serializer):
    date_lte = serializers.DateTimeField(default=None)
    date_gte = serializers.DateTimeField(default=None)
    search = serializers.CharField(
        default=None, help_text="A search query to filter entities"
    )
    unsafe = serializers.BooleanField(
        default=False,
        help_text="If true, entities considered as unsafe recommendations because of a"
        " low score or due to too few contributions will be included.",
    )
