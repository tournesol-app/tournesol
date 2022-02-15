from rest_framework.fields import IntegerField
from rest_framework.serializers import Serializer


class StatisticsSerializer(Serializer):
    """
    A representation of the Tournesol public statistics.
    """

    user_count = IntegerField()
    last_month_user_count = IntegerField()
    video_count = IntegerField()
    last_month_video_count = IntegerField()
    comparison_count = IntegerField()
    last_month_comparison_count = IntegerField()
