from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.serializers import ValidationError

from tournesol.models.poll import Poll
from tournesol.utils.video_language import ACCEPTED_LANGUAGE_CODES


class GenericPollUserSettingsSerializer(serializers.Serializer):
    """
    The settings common to all polls.
    """

    comparison__criteria_order = serializers.ListField(
        child=serializers.CharField(), required=False
    )
    rate_later__auto_remove = serializers.IntegerField(required=False)

    def validate_comparison__criteria_order(self, criteria):
        poll_name = self.context.get("poll_name", self._context["poll_name"])
        poll = Poll.objects.get(name=poll_name)

        if poll.main_criteria in criteria:
            raise ValidationError(_("The main criterion cannot be in the list."))

        if len(criteria) != len(set(criteria)):
            raise ValidationError(_("The list cannot contain duplicates."))

        for criterion in criteria:
            if criterion not in poll.criterias_list:
                raise ValidationError(
                    _("Unknown criterion: %(criterion)s.") % {"criterion": criterion}
                )

        return criteria

    def validate_rate_later__auto_remove(self, value):
        if value < 1:
            raise ValidationError(_("This parameter cannot be lower than 1."))
        return value


class VideosPollUserSettingsSerializer(GenericPollUserSettingsSerializer):
    """
    The settings specific to the `videos` poll.

    Also inherit the settings common to all polls.
    """

    DEFAULT_DATE_CHOICES = [
        ("TODAY", "today"),
        ("WEEK", "week"),
        ("MONTH", "month"),
        ("YEAR", "year"),
        ("ALL_TIME", "all_time"),
    ]

    recommendations__default_date = serializers.ChoiceField(
        choices=DEFAULT_DATE_CHOICES, allow_blank=True, required=False
    )
    recommendations__default_language = serializers.ListField(
        child=serializers.CharField(), required=False
    )
    recommendations__default_unsafe = serializers.BooleanField(required=False)

    def validate_recommendations__default_language(self, default_languages):
        for lang in default_languages:
            if lang not in ACCEPTED_LANGUAGE_CODES:
                raise ValidationError(_("Unknown language code: %(lang)s.") % {"lang": lang})

        return default_languages


class TournesolUserSettingsSerializer(serializers.Serializer):
    """A representation of all settings of the Tournesol project.

    This representation includes poll-agnostic settings in addition to the
    specific settings of each poll.
    """

    videos = VideosPollUserSettingsSerializer(required=False, context={"poll_name": "videos"})

    def create(self, validated_data):
        return validated_data

    def update(self, instance, validated_data):
        for scope, settings in self.validated_data.items():
            instance[scope].update(settings)
        return instance
