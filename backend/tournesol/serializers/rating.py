from django.db.models import Q
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework.exceptions import ValidationError
from rest_framework.fields import BooleanField, RegexField, SerializerMethodField
from rest_framework.serializers import ModelSerializer, Serializer

from core.utils.constants import YOUTUBE_VIDEO_ID_REGEX
from tournesol.models import ContributorRating, ContributorRatingCriteriaScore, Entity
from tournesol.serializers.entity import RelatedVideoSerializer, VideoSerializer


class ContributorCriteriaScore(ModelSerializer):
    class Meta:
        model = ContributorRatingCriteriaScore
        fields = ["criteria", "score", "uncertainty"]


class ContributorRatingSerializer(ModelSerializer):
    video = VideoSerializer(source="entity", read_only=True)
    criteria_scores = ContributorCriteriaScore(many=True, read_only=True)
    n_comparisons = SerializerMethodField(
        help_text="Number of comparisons submitted by the current user about the current video",
    )

    class Meta:
        model = ContributorRating
        fields = ["video", "is_public", "criteria_scores", "n_comparisons"]

    @extend_schema_field(OpenApiTypes.INT)
    def get_n_comparisons(self, obj):
        if hasattr(obj, "n_comparisons"):
            # Use annotated field if it has been defined by the queryset
            return obj.n_comparisons
        return obj.user.comparisons.filter(
            Q(entity_1=obj.entity) | Q(entity_2=obj.entity)
        ).count()


class ContributorRatingCreateSerializer(ContributorRatingSerializer):
    video_id = RegexField(YOUTUBE_VIDEO_ID_REGEX, write_only=True)

    class Meta:
        model = ContributorRating
        fields = ["video_id", "is_public", "video", "criteria_scores", "n_comparisons"]

    def validate(self, attrs):
        video_id = attrs.pop("video_id")
        video_serializer = RelatedVideoSerializer(data={"video_id": video_id})
        video_serializer.is_valid(raise_exception=True)
        video = Entity.objects.get(video_id=video_id)
        user = self.context["request"].user
        if user.contributorvideoratings.filter(entity=video).exists():
            raise ValidationError(
                "A ContributorRating already exists for this (user, video)",
                code="unique",
            )
        attrs["entity"] = video
        attrs["user"] = user
        return attrs


class ContributorRatingUpdateAllSerializer(Serializer):
    is_public = BooleanField()
