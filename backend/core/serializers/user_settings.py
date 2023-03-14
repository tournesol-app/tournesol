from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.serializers import ValidationError

from tournesol.models.poll import Poll


class GenericPollUserSettingsSerializer(serializers.Serializer):
    """
    The settings common to all polls.
    """

    criteria__display_order = serializers.ListField(child=serializers.CharField(), required=False)
    rate_later__auto_remove = serializers.IntegerField(required=False)

    def validate_criteria__display_order(self, criteria):
        poll_name = self.context.get("poll_name", self._context["poll_name"])
        poll = Poll.objects.get(name=poll_name)

        if len(criteria) != len(set(criteria)):
            raise ValidationError(
                _("Duplicate criteria in the list"),
                code="invalid",
            )

        if poll.main_criteria in criteria:
            raise ValidationError(
                _("Main poll criteria shouldn't be in the list"),
                code="invalid",
            )
        for criterion in criteria:
            if criterion not in poll.criterias_list:
                raise ValidationError(
                    _(f"Invalid criterion: {criterion}"),
                    code="invalid",
                )

        return criteria

    def validate_rate_later__auto_remove(self, value):
        if value < 1:
            raise ValidationError(_("This parameter cannot be lower than 1."))
        return value


class TournesolUserSettingsSerializer(serializers.Serializer):
    """A representation of all settings of the Tournesol project.

    This representation includes poll-agnostic settings in addition to the
    specific settings of each poll.
    """

    videos = GenericPollUserSettingsSerializer(required=False, context={"poll_name": "videos"})

    def create(self, validated_data):
        return validated_data

    def update(self, instance, validated_data):
        for scope, settings in self.validated_data.items():
            instance[scope].update(settings)
        return instance
