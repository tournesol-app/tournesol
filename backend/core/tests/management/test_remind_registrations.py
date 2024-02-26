from datetime import timedelta
from io import StringIO
from unittest import mock

from django.core.management import call_command
from django.test import TestCase

from core.tests.factories.user import UserFactory
from core.utils.time import time_ago
from tournesol.tests.factories.comparison import ComparisonFactory


@mock.patch("core.management.commands.remind_registrations.send_mail")
class RemindRegistrationTestCase(TestCase):
    def test_cmd_no_users(self, mock_send_mail):
        """
        When there is no users in the database, no notifications should be
        sent.
        """
        out = StringIO()
        call_command("remind_registrations", stdout=out)
        output = out.getvalue()

        mock_send_mail.assert_not_called()
        self.assertIn("users notified: 0", output)
        self.assertNotIn("some users have not been notified...", output)

    def test_cmd_with_users(self, mock_send_mail):
        """
        When there are users in the database, notifications should be sent to
        users that haven't made any comparison after a period following their
        registration.
        """
        out = StringIO()

        signup_date = time_ago(days=10)

        # Those users should be notified.
        user1 = UserFactory(username="no_contrib", is_active=True, date_joined=signup_date)
        user2 = UserFactory(username="contrib_at_signup1", is_active=True, date_joined=signup_date)
        user3 = UserFactory(username="contrib_at_signup2", is_active=True, date_joined=signup_date)

        # Those users should not be notified.
        user4 = UserFactory(
            username="contrib_after_signup",
            is_active=True,
            date_joined=signup_date
        )
        UserFactory(
            username="not_active",
            is_active=False,
            date_joined=signup_date
        )
        UserFactory(
            username="too_late",
            is_active=True,
            date_joined=signup_date - timedelta(days=1)
        )
        UserFactory(
            username="too_soon",
            is_active=True,
            date_joined=signup_date + timedelta(days=1)
        )

        contributions = {
            user1.pk: [],
            user2.pk: [signup_date + timedelta(hours=4)],
            user3.pk: [signup_date + timedelta(hours=16)],
            user4.pk: [signup_date + timedelta(hours=17)],
        }

        for user, dates in contributions.items():
            for date in dates:
                inst = ComparisonFactory(user_id=user)
                inst.datetime_add = date
                inst.save(update_fields=["datetime_add"])

        call_command("remind_registrations", stdout=out)
        output = out.getvalue()

        self.assertEqual(mock_send_mail.call_count, 3)
        self.assertIn("users notified: 3", output)
        self.assertNotIn("some users have not been notified...", output)
