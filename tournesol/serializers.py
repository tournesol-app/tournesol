"""
Serializer used by Tournesol's API
"""

from rest_framework.serializers import ModelSerializer, SerializerMethodField

from .models import Comparison, ComparisonCriteriaScore, Video, VideoRateLater, VideoCriteriaScore


class VideoSerializer(ModelSerializer):
    class Meta:
        model = Video
        fields = ["video_id"]


class VideoCriteriaScoreSerializer(ModelSerializer):
    class Meta:
        model = VideoCriteriaScore
        fields = "__all__"


class VideoRateLaterSerializer(ModelSerializer):
    video = VideoSerializer()

    class Meta:
        model = VideoRateLater
        fields = ["video"]


class ComparisonCriteriaScoreSerializer(ModelSerializer):
    class Meta:
        model = ComparisonCriteriaScore
        exclude = ["id"]


class ComparisonCriteriaScoreSerializerInverse(ModelSerializer):
    score = SerializerMethodField()

    class Meta:
        model = ComparisonCriteriaScore
        exclude = ["id"]

    def get_score(self, obj):
        """Returns the score of a comparison for a given criteria"""
        return obj.score * -1


class ComparisonSerializer(ModelSerializer):
    criteria_scores = ComparisonCriteriaScoreSerializer(many=True)
    video_1 = VideoSerializer()
    video_2 = VideoSerializer()

    class Meta:
        model = Comparison
        exclude = ["video_1_2_ids_sorted", "id"]


class ComparisonSerializerInverse(ModelSerializer):
    criteria_scores = ComparisonCriteriaScoreSerializerInverse(many=True)
    video_1 = SerializerMethodField()
    video_2 = SerializerMethodField()

    class Meta:
        model = Comparison
        exclude = ["video_1_2_ids_sorted", "id"]

    def get_video_1(self, obj):
        """Returns serialized first video of the comparison"""
        return VideoSerializer(obj.video_2).data

    def get_video_2(self, obj):
        """Returns serialized second video of the comparison"""
        return VideoSerializer(obj.video_1).data
