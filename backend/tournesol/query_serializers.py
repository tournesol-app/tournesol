from rest_framework import serializers


class RecommendationsFilterSerializer(serializers.Serializer):
    date_lte = serializers.DateTimeField(default=None)
    date_gte = serializers.DateTimeField(default=None)
    search = serializers.CharField(default=None)
    unsafe = serializers.BooleanField(default=False)
