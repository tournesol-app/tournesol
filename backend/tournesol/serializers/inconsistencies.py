from rest_framework import serializers
from rest_framework.serializers import Serializer


class ScoreInconsistencySerializer(Serializer):
    """
    Serializer for one element
    """
    inconsistency = serializers.FloatField()
    criterion = serializers.CharField()
    entity_1_uid = serializers.CharField()
    entity_2_uid = serializers.CharField()
    comparison_score = serializers.FloatField()
    entity_1_rating = serializers.FloatField()
    entity_2_rating = serializers.FloatField()


class ScoreInconsistenciesStatsSerializer(Serializer):
    """
    Return some statistics for each criterion,
    to be able to compare the results for the different criteria
    """
    mean_inconsistency = serializers.FloatField()
    inconsistent_comparisons_count = serializers.IntegerField()
    comparisons_count = serializers.IntegerField()


class ScoreInconsistenciesSerializer(Serializer):
    """
    Returns the score inconsistencies and some statistics.
    Used from a dictionary, not a queryset.
    """
    count = serializers.IntegerField()
    results = ScoreInconsistencySerializer(many=True)
    stats = serializers.DictField(child=ScoreInconsistenciesStatsSerializer(), label="criterion")


class ScoreInconsistenciesFilterSerializer(Serializer):

    inconsistency_threshold = serializers.FloatField(
        default=5.0,
        help_text="Comparisons with an inconsistency score above this threshold are "
                  "considered inconsistent and listed in the response (max. 100 responses).",
    )

    date_gte = serializers.DateTimeField(
        default=None,
        help_text="Restrict the search to entities created or edited after this date.\n"
                  "Accepted formats: ISO 8601 datetime (e.g `2021-12-01T12:45:00`).",
    )
