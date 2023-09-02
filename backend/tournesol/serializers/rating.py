from drf_spectacular.utils import extend_schema_serializer
from rest_framework.exceptions import ValidationError
from rest_framework.fields import BooleanField, CharField, DateTimeField, IntegerField
from rest_framework.serializers import ModelSerializer, Serializer

from tournesol.models import ContributorRating, ContributorRatingCriteriaScore
from tournesol.serializers.entity import EntityNoExtraFieldSerializer, RelatedEntitySerializer
from tournesol.serializers.poll import CollectiveRatingSerializer, IndividualRatingSerializer


class ContributorCriteriaScore(ModelSerializer):
    class Meta:
        model = ContributorRatingCriteriaScore
        fields = ["criteria", "score", "uncertainty"]


class ExtendedInvididualRatingSerializer(IndividualRatingSerializer):
    criteria_scores = ContributorCriteriaScore(many=True, read_only=True)
    last_compared_at = DateTimeField(read_only=True, allow_null=True)

    class Meta:
        model = ContributorRating
        fields = IndividualRatingSerializer.Meta.fields + ["criteria_scores", "last_compared_at"]
        read_only_fields = fields


@extend_schema_serializer(
    deprecate_fields=["n_comparisons", "last_compared_at", "is_public", "criteria_scores"]
)
class ContributorRatingSerializer(ModelSerializer):
    entity = EntityNoExtraFieldSerializer(read_only=True)
    individual_rating = ExtendedInvididualRatingSerializer(source="*", read_only=True)
    collective_rating = CollectiveRatingSerializer(
        source="entity.single_poll_rating",
        read_only=True,
        allow_null=True
    )
    criteria_scores = ContributorCriteriaScore(many=True, read_only=True)
    n_comparisons = IntegerField(
        default=0,
        read_only=True,
        help_text="Number of comparisons submitted by the current user about the current video",
    )
    last_compared_at = DateTimeField(read_only=True, default=None, required=False)

    class Meta:
        model = ContributorRating
        fields = [
            "entity",
            "individual_rating",
            "collective_rating",
            "is_public",
            "criteria_scores",
            "n_comparisons",
            "last_compared_at",
        ]

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
        fields = [
            "uid",
            "is_public",
            "entity",
            "criteria_scores",
            "n_comparisons",
            "last_compared_at",
            "individual_rating",
            "collective_rating",
        ]

    def validate(self, attrs):
        uid = attrs.pop("uid")
        entity_serializer = RelatedEntitySerializer(data={"uid": uid}, context=self.context)
        entity_serializer.is_valid(raise_exception=True)
        entity_id = entity_serializer.validated_data["pk"]

        poll = self.context["poll"]
        user = self.context["request"].user
        if user.contributorvideoratings.filter(poll=poll, entity_id=entity_id).exists():
            raise ValidationError(
                "A ContributorRating already exists for this (user, entity, poll)",
                code="unique",
            )
        attrs["entity_id"] = entity_id
        attrs["user"] = user
        return attrs


class ContributorRatingUpdateAllSerializer(Serializer):
    is_public = BooleanField()
