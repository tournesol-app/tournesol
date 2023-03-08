from django.core.exceptions import ValidationError
from django.test import TestCase

from core.models.user import User
from core.tests.factories.user import UserFactory


class UserModelTestCase(TestCase):
    """
    TestCase of the User model.
    """

    def test_default_settings(self):
        """
        The users must be created with an empty set of settings representing
        their preferences.
        """
        UserFactory(username="user")
        user = User.objects.get(username="user")

        self.assertEqual(user.settings, {})

    def test_validate_email_unique_with_plus_rsplit(self):
        """
        The method must correctly split on the last `@` character.
        """
        already_used = "already@USED+tournesol@example.org"
        UserFactory(email=already_used)

        for email in [
            "already@used+@example.org",
            "already@used+@EXAMPLE.org",
            "ALREADY@USED+tournesol@example.org",
            "already@used+TOURNESOL@example.org",
            "already@used+different@example.org",
            "already@used+foo+bar@example.org",
        ]:
            with self.assertRaises(ValidationError):
                User.validate_email_unique_with_plus(email)
