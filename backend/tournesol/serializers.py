"""
Serializer used by Tournesol's API
"""

from django.db import transaction
from django.db.models import ObjectDoesNotExist

from rest_framework import serializers
from rest_framework.serializers import Serializer, ModelSerializer

from .models import (
    Comparison, ComparisonCriteriaScore, Video, VideoRateLater,
    VideoCriteriaScore, ContributorRating, ContributorRatingCriteriaScore, Tag
)


class VideoSerializer(ModelSerializer):

    class Meta:
        model = Video
        fields = [
            "video_id",
            "name",
            "description",
            "publication_date",
            "views",
            "uploader",
            "language",
            "rating_n_ratings",
            "rating_n_contributors",
        ]
        read_only_fields = [
            "name",
            "description",
            "publication_date",
            "views",
            "uploader",
            "language",
            "rating_n_ratings",
            "rating_n_contributors",
        ]

    def save(self, **kwargs):
        tags = kwargs.pop('tags', [])
        video = super().save(**kwargs)
        for tag_name in tags:
            #  The return object is a tuple having first an instance of Tag, and secondly a bool
            tag = Tag.objects.get_or_create(name=tag_name)
            video.tags.add(tag[0].id)
        return video


class VideoReadOnlySerializer(Serializer):
    """
    A video serializer without all the Video model auto-validations.

    Used by ModelSerializer(s) having one or more nested relations with Video,
    and having the constraint of not creating new videos in database when
    creating new objects.

    ex: adding a new Comparison shouldn't create new Video in the database
    """
    video_id = serializers.CharField(
        max_length=20
    )

    class Meta:
        fields = ["video_id"]

    def validate_video_id(self, value):
        try:
            Video.objects.get(video_id=value)
        except ObjectDoesNotExist:
            raise serializers.ValidationError(
                "The video with id '{}' does not exist.".format(value)
            )

        return value


class VideoCriteriaScoreSerializer(ModelSerializer):
    class Meta:
        model = VideoCriteriaScore
        fields = ["criteria", "score", "uncertainty", "quantile"]


class VideoSerializerWithCriteria(ModelSerializer):
    criteria_scores = VideoCriteriaScoreSerializer(many=True)

    class Meta:
        model = Video
        fields = [
            "video_id",
            "name",
            "description",
            "publication_date",
            "views",
            "uploader",
            "criteria_scores",
            "language",
            "rating_n_ratings",
            "rating_n_contributors",
        ]


class VideoRateLaterSerializer(ModelSerializer):
    video = VideoSerializer()

    class Meta:
        model = VideoRateLater
        fields = ["video"]


class ComparisonCriteriaScoreSerializer(ModelSerializer):
    class Meta:
        model = ComparisonCriteriaScore
        fields = ["criteria", "score", "weight"]


class ComparisonSerializerMixin:
    def reverse_criteria_scores(self, criteria_scores):
        opposite_scores = criteria_scores.copy()
        for index, score in enumerate(criteria_scores):
            opposite_scores[index]["score"] = score["score"] * -1

        return opposite_scores


class ComparisonSerializer(ComparisonSerializerMixin, ModelSerializer):
    """
    A comparison serializer used for the operations create, retrieve and list.

    Given the context determined by the view, it will represent the comparison
    in the reverse order.

    Use `ComparisonUpdateSerializer` for the update operation.
    """
    video_a = VideoReadOnlySerializer(source="video_1")
    video_b = VideoReadOnlySerializer(source="video_2")
    criteria_scores = ComparisonCriteriaScoreSerializer(many=True)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Comparison
        fields = [
            "user", "video_a", "video_b", "criteria_scores", "duration_ms"
        ]

    def to_representation(self, instance):
        """
        Display the opposite of each criteria scores if the comparison is
        requested in the reverse order.
        """
        ret = super(ComparisonSerializer, self).to_representation(instance)

        if self.context.get("reverse", False):
            ret["video_a"], ret["video_b"] = ret["video_b"], ret["video_a"]
            ret["criteria_scores"] = self.reverse_criteria_scores(
                ret["criteria_scores"]
            )

        return ret

    @transaction.atomic
    def create(self, validated_data):
        video_id_1 = validated_data.get("video_1").get("video_id")
        video_id_2 = validated_data.get("video_2").get("video_id")
        # the validation performed by the VideoReadOnlySerializer guarantees
        # that the video submitted exist in the database
        video_1 = Video.objects.get(video_id=video_id_1)
        video_2 = Video.objects.get(video_id=video_id_2)

        # get default values directly from the model
        default_duration_ms = Comparison._meta.get_field("duration_ms").get_default()

        comparison = Comparison.objects.create(
            video_1=video_1, video_2=video_2, user=validated_data.get("user"),
            duration_ms=validated_data.get("duration_ms", default_duration_ms)
        )

        for criteria_score in validated_data.pop("criteria_scores"):
            ComparisonCriteriaScore.objects.create(
                comparison=comparison,
                **criteria_score
            )

        return comparison


class ComparisonUpdateSerializer(ComparisonSerializerMixin, ModelSerializer):
    """
    A comparison serializer used only for updates.

    Given the context determined by the view, it will represent or save the
    comparison in the reverse order.

    Use `ComparisonSerializer` for all other operations.
    """
    criteria_scores = ComparisonCriteriaScoreSerializer(many=True)

    class Meta:
        model = Comparison
        fields = [
            "criteria_scores", "duration_ms"
        ]

    def to_representation(self, instance):
        """
        Display the opposite of each criteria scores if the comparison is
        requested in the reverse order.

        Also add `video_a` and `video_b` fields to make the representation
        consistent across all comparison serializers.
        """
        ret = super(
            ComparisonUpdateSerializer,
            self
        ).to_representation(instance)

        video_1_repr = VideoReadOnlySerializer().to_representation(instance.video_1)
        video_2_repr = VideoReadOnlySerializer().to_representation(instance.video_2)
        ret["video_a"], ret["video_b"] = video_1_repr, video_2_repr

        if self.context.get("reverse", False):
            ret["video_a"], ret["video_b"] = ret["video_b"], ret["video_a"]
            ret["criteria_scores"] = self.reverse_criteria_scores(
                ret["criteria_scores"]
            )

        ret.move_to_end("video_b", last=False)
        ret.move_to_end("video_a", last=False)
        return ret

    def to_internal_value(self, data):
        """
        Save the comparison in the order expected by the model, even if the
        comparison is provided reversed.
        """
        ret = super(ComparisonUpdateSerializer, self).to_internal_value(data)

        if self.context.get("reverse", False):
            ret["criteria_scores"] = self.reverse_criteria_scores(
                ret["criteria_scores"]
            )
        return ret

    @transaction.atomic
    def update(self, instance, validated_data):
        if validated_data.get("duration_ms"):
            instance.duration_ms = validated_data.get("duration_ms")

        instance.save()
        instance.criteria_scores.all().delete()

        for criteria_score in validated_data.pop("criteria_scores"):
            instance.criteria_scores.create(**criteria_score)

        return instance


class ContributorCriteriaScore(ModelSerializer):
    class Meta:
        model = ContributorRatingCriteriaScore
        fields = ["criteria", "score", "uncertainty"]


class ContributorRatingSerializer(ModelSerializer):
    video = VideoSerializer(read_only=True)
    criteria_scores = ContributorCriteriaScore(many=True, read_only=True)

    class Meta:
        model = ContributorRating
        fields = ["video", "is_public", "criteria_scores"]
