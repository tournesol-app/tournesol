from rest_framework.fields import CharField, IntegerField
from rest_framework.serializers import Serializer


class ActiveUsersStatisticsSerializer(Serializer):
    total = IntegerField()
    joined_last_month = IntegerField()
    joined_last_30_days = IntegerField()


class ComparedEntitiesStatisticsSerializer(Serializer):
    total = IntegerField()
    added_last_month = IntegerField()
    added_last_30_days = IntegerField()


class ComparisonsStatisticsSerializer(Serializer):
    total = IntegerField()
    added_last_month = IntegerField()  # Kept for backward compatibility, use last_30_days instead.
    added_last_30_days = IntegerField()
    added_current_week = IntegerField()


class PollStatisticsSerializer(Serializer):
    name = CharField()
    compared_entities = ComparedEntitiesStatisticsSerializer()
    comparisons = ComparisonsStatisticsSerializer()


class StatisticsSerializer(Serializer):
    """
    A representation of the Tournesol public statistics.
    """

    active_users = ActiveUsersStatisticsSerializer()
    polls = PollStatisticsSerializer(many=True)
