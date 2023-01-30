from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.serializers import ValidationError


class GenericPollUserSettingsSerializer(serializers.Serializer):
    """
    The settings common to all polls.
    """

    rate_later__auto_remove = serializers.IntegerField(required=False)

    def validate_rate_later__auto_remove(self, value):
        if value < 1:
            raise ValidationError(_("This parameter cannot be lower than 1."))
        return value


class TournesolUserSettingsSerializer(serializers.Serializer):
    """A representation of all settings of the Tournesol project.

    This representation includes poll-agnostic settings in addition to the
    specific settings of each poll.
    """

    videos = GenericPollUserSettingsSerializer(required=False)

    def create(self, validated_data):
        return validated_data

    def update(self, instance, validated_data):
        for scope, settings in self.validated_data.items():
            instance[scope].update(settings)
        return instance
