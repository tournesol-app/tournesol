from rest_framework.exceptions import ValidationError
from rest_framework.fields import BooleanField, CharField, DateTimeField
from rest_framework.serializers import ModelSerializer, Serializer

from tournesol.models import ContributorRating
from tournesol.serializers.criteria_score import ContributorCriteriaScoreSerializer
from tournesol.serializers.entity import EntityNoExtraFieldSerializer, RelatedEntitySerializer
from tournesol.serializers.entity_context import EntityContextSerializer
from tournesol.serializers.poll import CollectiveRatingSerializer, IndividualRatingSerializer


class ExtendedInvididualRatingSerializer(IndividualRatingSerializer):
    criteria_scores = ContributorCriteriaScoreSerializer(many=True, read_only=True)
    last_compared_at = DateTimeField(read_only=True, allow_null=True)

    class Meta:
        model = ContributorRating
        fields = IndividualRatingSerializer.Meta.fields + ["criteria_scores", "last_compared_at"]
        read_only_fields = fields


class ContributorRatingSerializer(ModelSerializer):
    entity = EntityNoExtraFieldSerializer(read_only=True)
    entity_contexts = EntityContextSerializer(
        source="entity.single_poll_entity_contexts",
        read_only=True,
        many=True
    )
    individual_rating = ExtendedInvididualRatingSerializer(source="*", read_only=True)
    collective_rating = CollectiveRatingSerializer(
        source="entity.single_poll_rating",
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = ContributorRating
        fields = [
            "entity",
            "entity_contexts",
            "individual_rating",
            "collective_rating",
            "is_public",
        ]
        extra_kwargs = {"is_public": {"write_only": True}}

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
            "entity_contexts",
            "individual_rating",
            "collective_rating",
        ]
        extra_kwargs = ContributorRatingSerializer.Meta.extra_kwargs

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
