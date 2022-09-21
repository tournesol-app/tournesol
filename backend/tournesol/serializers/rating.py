from django.db.models import Q
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework.exceptions import ValidationError
from rest_framework.fields import BooleanField, CharField, SerializerMethodField
from rest_framework.serializers import ModelSerializer, Serializer

from tournesol.models import ContributorRating, ContributorRatingCriteriaScore, Entity
from tournesol.serializers.entity import EntityNoExtraFieldSerializer, RelatedEntitySerializer


class ContributorCriteriaScore(ModelSerializer):
    class Meta:
        model = ContributorRatingCriteriaScore
        fields = ["criteria", "score", "uncertainty"]


class ContributorRatingSerializer(ModelSerializer):
    entity = EntityNoExtraFieldSerializer(read_only=True)
    criteria_scores = ContributorCriteriaScore(many=True, read_only=True)
    n_comparisons = SerializerMethodField(
        help_text="Number of comparisons submitted by the current user about the current video",
    )

    class Meta:
        model = ContributorRating
        fields = ["entity", "is_public", "criteria_scores", "n_comparisons"]

    @extend_schema_field(OpenApiTypes.INT)
    def get_n_comparisons(self, obj):
        """
        The number of comparisons is always computed for a specific poll for
        now.
        """
        if hasattr(obj, "n_comparisons"):
            # Use annotated field if it has been defined by the queryset
            return obj.n_comparisons
        return obj.user.comparisons.filter(
            Q(poll=self.context["poll"])
            & (Q(entity_1=obj.entity) | Q(entity_2=obj.entity))
        ).count()

    def to_internal_value(self, data):
        """
        Determine the poll according to the context provided by the view.
        """
        ret = super().to_internal_value(data)
        ret["poll_id"] = self.context.get("poll").id
        return ret


class ContributorRatingCreateSerializer(ContributorRatingSerializer):
    uid = CharField(max_length=144, write_only=True)

    class Meta:
        model = ContributorRating
        fields = ["uid", "is_public", "entity", "criteria_scores", "n_comparisons"]

    def validate(self, attrs):
        uid = attrs.pop("uid")
        entity_serializer = RelatedEntitySerializer(
            data={"uid": uid}, context=self.context
        )
        entity_serializer.is_valid(raise_exception=True)
        entity = Entity.objects.get(uid=uid)

        poll = self.context["poll"]
        user = self.context["request"].user
        if user.contributorvideoratings.filter(poll=poll, entity=entity).exists():
            raise ValidationError(
                "A ContributorRating already exists for this (user, entity, poll)",
                code="unique",
            )
        attrs["entity"] = entity
        attrs["user"] = user
        return attrs


class ContributorRatingUpdateAllSerializer(Serializer):
    is_public = BooleanField()
