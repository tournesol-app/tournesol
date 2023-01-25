from django.test import TestCase

from core.serializers.user_settings import GenericPollUserSettingsSerializer


class GenericPollUserSettingsSerializerTestCase(TestCase):
    """
    TestCase of the `GenericPollUserSettingsSerializer` serializer.
    """

    def test_validate_rate_later__auto_remove(self):
        """
        The `rate_later__auto_remove` setting shouldn't be less than 2.
        """
        serializer = GenericPollUserSettingsSerializer(
            data={"rate_later__auto_remove": -1}
        )
        self.assertEqual(serializer.is_valid(), False)
        self.assertIn("rate_later__auto_remove", serializer.errors)

        serializer = GenericPollUserSettingsSerializer(
            data={"rate_later__auto_remove": 1}
        )
        self.assertEqual(serializer.is_valid(), False)
        self.assertIn("rate_later__auto_remove", serializer.errors)

        serializer = GenericPollUserSettingsSerializer(
            data={"rate_later__auto_remove": 2}
        )
        self.assertEqual(serializer.is_valid(), True)

        serializer = GenericPollUserSettingsSerializer(
            data={"rate_later__auto_remove": 99}
        )
        self.assertEqual(serializer.is_valid(), True)
