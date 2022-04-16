from rest_framework import serializers
from rest_framework.serializers import Serializer


class ScoreInconsistencySerializer(Serializer):
    """
    Serializer for one element
    """

    inconsistency = serializers.FloatField()
    entity_1_uid = serializers.CharField()
    entity_2_uid = serializers.CharField()
    criteria = serializers.CharField()
    comparison_score = serializers.FloatField()
    entity_1_rating = serializers.FloatField()
    entity_2_rating = serializers.FloatField()


class ScoreInconsistenciesSerializer(Serializer):
    """
    Returns the score inconsistencies and related data.
    Used from a dictionary, not a queryset.
    The count is exhaustive, but the results list is truncated at 100 elements.
    """
    mean_inconsistency = serializers.FloatField()
    count = serializers.IntegerField()
    results = ScoreInconsistencySerializer(many=True)


class ScoreInconsistenciesFilterSerializer(serializers.Serializer):

    inconsistency_threshold = serializers.FloatField(
        default=5.0,
        help_text="Comparisons with an inconsistency score above this threshold are "
                  "considered inconsistent and listed in the response (max. 100 responses)",
    )

    date_gte = serializers.DateTimeField(
        default=None,
        help_text="Restrict the search to entities created or edited after this date"
                  "Accepted formats: ISO 8601 datetime (e.g `2021-12-01T12:45:00`) ",
    )
