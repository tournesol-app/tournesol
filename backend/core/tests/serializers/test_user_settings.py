import random

from django.test import TestCase

from core.serializers.user_settings import GenericPollUserSettingsSerializer
from tournesol.models.poll import Poll


class GenericPollUserSettingsSerializerTestCase(TestCase):
    """
    TestCase of the `GenericPollUserSettingsSerializer` serializer.
    """

    def test_validate_criteria__display_order(self):
        """
        The `validate_criteria__display_order` setting must match existing poll criteria.
        """

        poll = Poll.default_poll()
        secondary_criteria_list = poll.criterias_list.copy()
        secondary_criteria_list.remove(poll.main_criteria)

        context = {'poll_name': poll.name}

        serializer = GenericPollUserSettingsSerializer(
            context=context,
            data={"criteria__display_order": ["not_a_criteria"]}
        )
        self.assertEqual(serializer.is_valid(), False)
        self.assertIn("criteria__display_order", serializer.errors)

        serializer = GenericPollUserSettingsSerializer(
            context=context,
            data={"criteria__display_order": [secondary_criteria_list[0], "not_a_criteria"]}
        )
        self.assertEqual(serializer.is_valid(), False)
        self.assertIn("criteria__display_order", serializer.errors)

        serializer = GenericPollUserSettingsSerializer(
            context=context,
            data={"criteria__display_order": []}
        )
        self.assertEqual(serializer.is_valid(), True)

        serializer = GenericPollUserSettingsSerializer(
            context=context,
            data={"criteria__display_order": [secondary_criteria_list[1]]}
        )
        self.assertEqual(serializer.is_valid(), True)

        serializer = GenericPollUserSettingsSerializer(
            context=context,
            data={"criteria__display_order": secondary_criteria_list[0:3]}
        )
        self.assertEqual(serializer.is_valid(), True)

        # Test main criteria should not be in the list
        serializer = GenericPollUserSettingsSerializer(
            context=context,
            data={"criteria__display_order": [poll.main_criteria]}
        )
        self.assertEqual(serializer.is_valid(), False)

        # Test one duplicate criteria
        serializer = GenericPollUserSettingsSerializer(
            context=context,
            data={"criteria__display_order": [secondary_criteria_list[0], secondary_criteria_list[0], secondary_criteria_list[1]]}
        )
        self.assertEqual(serializer.is_valid(), False)

        # Test all criteria in random order
        random.shuffle(secondary_criteria_list)
        serializer = GenericPollUserSettingsSerializer(
            context=context,
            data={"criteria__display_order": secondary_criteria_list}

        )
        self.assertEqual(serializer.is_valid(), True)
        
    def test_validate_rate_later__auto_remove(self):
        """
        The `rate_later__auto_remove` setting must be strictly positive.
        """
        serializer = GenericPollUserSettingsSerializer(
            data={"rate_later__auto_remove": -1}
        )
        self.assertEqual(serializer.is_valid(), False)
        self.assertIn("rate_later__auto_remove", serializer.errors)

        serializer = GenericPollUserSettingsSerializer(
            data={"rate_later__auto_remove": 0}
        )
        self.assertEqual(serializer.is_valid(), False)
        self.assertIn("rate_later__auto_remove", serializer.errors)

        serializer = GenericPollUserSettingsSerializer(
            data={"rate_later__auto_remove": 1}
        )
        self.assertEqual(serializer.is_valid(), True)

        serializer = GenericPollUserSettingsSerializer(
            data={"rate_later__auto_remove": 99}
        )
        self.assertEqual(serializer.is_valid(), True)
