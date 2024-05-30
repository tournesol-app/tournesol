from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.serializers import ValidationError

from tournesol.models.poll import Poll
from tournesol.utils.video_language import ACCEPTED_LANGUAGE_CODES


class GeneralUserSettingsSerializer(serializers.Serializer):
    """
    The general user settings that are not related to Tournesol polls.
    """

    # The first element of the tuple should be an ISO 639-1 code.
    NOTIFICATIONS_LANG = [
        ("en", "en"),
        ("fr", "fr"),
    ]

    notifications__lang = serializers.ChoiceField(
        choices=NOTIFICATIONS_LANG, required=False
    )
    notifications_email__research = serializers.BooleanField(required=False)
    notifications_email__new_features = serializers.BooleanField(required=False)


class GenericPollUserSettingsSerializer(serializers.Serializer):
    """
    The settings common to each poll.
    """

    COMPONENT_DISPLAY_STATE = [
        ("ALWAYS", "always"),
        ("EMBEDDED_ONLY", "embedded_only"),
        ("WEBSITE_ONLY", "website_only"),
        ("NEVER", "never"),
    ]

    comparison__auto_select_entities = serializers.BooleanField(required=False)
    comparison__criteria_order = serializers.ListField(
        child=serializers.CharField(), required=False
    )

    comparison_ui__weekly_collective_goal_display = serializers.ChoiceField(
        choices=COMPONENT_DISPLAY_STATE, allow_blank=True, required=False
    )
    comparison_ui__weekly_collective_goal_mobile = serializers.BooleanField(required=False)

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

    Also inherit the settings common to each poll.
    """

    DEFAULT_DATE_CHOICES = [
        ("TODAY", "today"),
        ("WEEK", "week"),
        ("MONTH", "month"),
        ("YEAR", "year"),
        ("ALL_TIME", "all_time"),
    ]

    extension__search_reco = serializers.BooleanField(
        required=False,
        help_text=(
            "Whether Tournesol recommendations should be integrated in Youtube.com search results."
        ),
    )

    recommendations__default_date = serializers.ChoiceField(
        choices=DEFAULT_DATE_CHOICES, allow_blank=True, required=False
    )
    recommendations__default_languages = serializers.ListField(
        child=serializers.CharField(), allow_empty=True, required=False
    )
    recommendations__default_unsafe = serializers.BooleanField(required=False)
    recommendations__default_exclude_compared_entities = serializers.BooleanField(required=False)

    def validate_recommendations__default_languages(self, default_languages):
        for lang in default_languages:
            if lang not in ACCEPTED_LANGUAGE_CODES:
                raise ValidationError(_("Unknown language code: %(lang)s.") % {"lang": lang})

        return default_languages


class TournesolUserSettingsSerializer(serializers.Serializer):
    """
    A representation of all user settings of the Tournesol project.

    This representation includes poll-agnostic settings in addition to the
    specific settings of each poll.
    """

    general = GeneralUserSettingsSerializer(required=False)
    videos = VideosPollUserSettingsSerializer(required=False, context={"poll_name": "videos"})

    def create(self, validated_data):
        return validated_data

    def update(self, instance, validated_data):
        for scope, settings in self.validated_data.items():
            if scope not in instance:
                instance[scope] = {}
            instance[scope].update(settings)
        return instance
