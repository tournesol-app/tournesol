import random

from django.test import TestCase

from core.serializers.user_settings import (
    GenericPollUserSettingsSerializer,
    VideosPollUserSettingsSerializer,
)
from tournesol.models.poll import Poll


class GenericPollUserSettingsSerializerTestCase(TestCase):
    """
    TestCase of the `GenericPollUserSettingsSerializer` serializer.
    """

    def validate_comparison__criteria_order(self):
        """
        The `validate_comparison__criteria_order` setting must match the related poll's criteria.
        """

        poll = Poll.default_poll()
        secondary_criteria_list = poll.criterias_list.copy()
        secondary_criteria_list.remove(poll.main_criteria)

        context = {"poll_name": poll.name}

        # A non-existing criterion should be invalid.
        serializer = GenericPollUserSettingsSerializer(
            context=context, data={"comparison__criteria_order": ["not_a_criterion"]}
        )
        self.assertEqual(serializer.is_valid(), False)
        self.assertIn("comparison__criteria_order", serializer.errors)

        # A combination of existing and non-existing criteria should be invalid.
        serializer = GenericPollUserSettingsSerializer(
            context=context,
            data={"comparison__criteria_order": [secondary_criteria_list[0], "not_a_criteria"]},
        )
        self.assertEqual(serializer.is_valid(), False)
        self.assertIn("comparison__criteria_order", serializer.errors)

        # The main criterion should be invalid.
        serializer = GenericPollUserSettingsSerializer(
            context=context, data={"comparison__criteria_order": [poll.main_criteria]}
        )
        self.assertEqual(serializer.is_valid(), False)

        # A duplicated criterion should be invalid
        serializer = GenericPollUserSettingsSerializer(
            context=context,
            data={
                "comparison__criteria_order": [
                    secondary_criteria_list[0],
                    secondary_criteria_list[0],
                ]
            },
        )
        self.assertEqual(serializer.is_valid(), False)

        # An empty list is valid.
        serializer = GenericPollUserSettingsSerializer(
            context=context, data={"comparison__criteria_order": []}
        )
        self.assertEqual(serializer.is_valid(), True)

        # An existing criterion is valid.
        serializer = GenericPollUserSettingsSerializer(
            context=context, data={"comparison__criteria_order": [secondary_criteria_list[0]]}
        )
        self.assertEqual(serializer.is_valid(), True)

        # A list of existing criterion is valid.
        serializer = GenericPollUserSettingsSerializer(
            context=context, data={"comparison__criteria_order": secondary_criteria_list[0:3]}
        )
        self.assertEqual(serializer.is_valid(), True)

        # A random order of the existing criteria is valid.
        random.shuffle(secondary_criteria_list)
        serializer = GenericPollUserSettingsSerializer(
            context=context, data={"comparison__criteria_order": secondary_criteria_list}
        )
        self.assertEqual(serializer.is_valid(), True)

    def test_validate_rate_later__auto_remove(self):
        """
        The `rate_later__auto_remove` setting must be strictly positive.
        """
        serializer = GenericPollUserSettingsSerializer(data={"rate_later__auto_remove": -1})
        self.assertEqual(serializer.is_valid(), False)
        self.assertIn("rate_later__auto_remove", serializer.errors)

        serializer = GenericPollUserSettingsSerializer(data={"rate_later__auto_remove": 0})
        self.assertEqual(serializer.is_valid(), False)
        self.assertIn("rate_later__auto_remove", serializer.errors)

        serializer = GenericPollUserSettingsSerializer(data={"rate_later__auto_remove": 1})
        self.assertEqual(serializer.is_valid(), True)

        serializer = GenericPollUserSettingsSerializer(data={"rate_later__auto_remove": 99})
        self.assertEqual(serializer.is_valid(), True)


class VideosPollUserSettingsSerializerTestCase(TestCase):
    """
    TestCase of the `VideosPollUserSettingsSerializer` serializer.
    """

    def test_validate_recommendations__default_languages(self):
        """
        The `validate_recommendations__default_languages` setting must raise
        an error for unknown languages.
        """

        serializer = VideosPollUserSettingsSerializer(
            data={"recommendations__default_languages": []}
        )
        self.assertEqual(serializer.is_valid(), True)

        serializer = VideosPollUserSettingsSerializer(
            data={"recommendations__default_languages": ["fr"]}
        )
        self.assertEqual(serializer.is_valid(), True)

        serializer = VideosPollUserSettingsSerializer(
            data={"recommendations__default_languages": ["fr", "en"]}
        )
        self.assertEqual(serializer.is_valid(), True)

        serializer = VideosPollUserSettingsSerializer(
            data={"recommendations__default_languages": ["not_a_language"]}
        )
        self.assertEqual(serializer.is_valid(), False)
        self.assertIn("recommendations__default_languages", serializer.errors)

        serializer = VideosPollUserSettingsSerializer(
            data={"recommendations__default_languages": ["en", "not_a_language"]}
        )
        self.assertEqual(serializer.is_valid(), False)
        self.assertIn("recommendations__default_languages", serializer.errors)

    def test_validate_recommendations__default_date(self):
        """
        The `validate_recommendations__default_date` setting must accept only
        a specific set of date.
        """

        for date in ["TODAY", "WEEK", "MONTH", "YEAR", "ALL_TIME"]:
            serializer = VideosPollUserSettingsSerializer(
                data={"recommendations__default_date": date}
            )
            self.assertEqual(serializer.is_valid(), True)

        # A blank value means no default date.
        serializer = VideosPollUserSettingsSerializer(data={"recommendations__default_date": ""})
        self.assertEqual(serializer.is_valid(), True)

        serializer = VideosPollUserSettingsSerializer(
            data={"recommendations__default_date": ["not_a_valid_date"]}
        )
        self.assertEqual(serializer.is_valid(), False)
        self.assertIn("recommendations__default_date", serializer.errors)
