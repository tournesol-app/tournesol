import re

from django.db import IntegrityError
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from tournesol.entities.base import UID_DELIMITER
from tournesol.errors import ConflictError
from tournesol.models.entity_source import UID_REGEX_BY_NAMESPACE, EntitySource, SourceNotFound
from tournesol.models.subscription import Subscription


class RelatedEntitySourceSerializer(ModelSerializer):
    """
    An `EntitySource` serializer exposing the source of a subscription.

    Only the field `uid` is provided when using write HTTP methods; the source
    itself is looked up or created when the subscription is saved.
    """

    uid = serializers.CharField(max_length=144)

    class Meta:
        model = EntitySource
        fields = ["uid", "metadata"]
        read_only_fields = ["metadata"]

    def validate_uid(self, value):
        namespace = value.split(UID_DELIMITER)[0]
        uid_regex = UID_REGEX_BY_NAMESPACE.get(namespace)

        if uid_regex is None:
            raise serializers.ValidationError(f"Unknown `uid` namespace: {namespace}")

        if not re.fullmatch(uid_regex, value):
            raise serializers.ValidationError(
                "This value does not match the required pattern."
            )

        return value


class SubscriptionSerializer(ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    entity_source = RelatedEntitySourceSerializer()

    class Meta:
        model = Subscription
        fields = ["user", "entity_source", "created_at"]
        read_only_fields = ["created_at"]

        # The nested `entity_source` is a dict at validation time, so the
        # automatic (user, entity_source) uniqueness validator cannot run. The
        # conflict is detected on the database constraint in `create` instead.
        validators = []

    def create(self, validated_data):
        uid = validated_data.pop("entity_source")["uid"]
        try:
            source = EntitySource.get_or_create_from_uid(uid)
        except SourceNotFound as error:
            raise serializers.ValidationError(
                {"entity_source": {"uid": [_("This source does not exist.")]}}
            ) from error

        try:
            return Subscription.objects.create(
                entity_source=source,
                **validated_data,
            )
        except IntegrityError as error:
            raise ConflictError(
                _("You are already subscribed to this source.")
            ) from error
