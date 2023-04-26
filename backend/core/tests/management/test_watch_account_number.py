from datetime import timedelta
from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from core.models.user import EmailDomain
from core.tests.factories.user import UserFactory
from tournesol.tests.utils.mock_now import MockNow


class WatchAccountNumberTestCase(TestCase):
    @MockNow.Context()
    def setUp(self):
        today = timezone.now()

        # Create 6 domains: 3 trusted and 3 not-trusted with 9, 10 and 11 users.
        for n in range(1, 4):
            EmailDomain.objects.create(
                domain=f"@trusted_{n}.test", status=EmailDomain.STATUS_ACCEPTED
            )
            EmailDomain.objects.create(
                domain=f"@not_trusted_{n}.test", status=EmailDomain.STATUS_REJECTED
            )

        # The domain trusted_1 should contain fewer users that the first threshold.
        for i in range(9):
            UserFactory(email=f"user{i}@trusted_1.test", date_joined=today)
            UserFactory(email=f"user{i}@not_trusted_1.test", date_joined=today)

        # The domain trusted_2 should contain exactly as many users as the first threshold.
        for i in range(10):
            UserFactory(email=f"user{i}@trusted_2.test", date_joined=today)
            UserFactory(email=f"user{i}@not_trusted_2.test", date_joined=today)

        # The domain trusted_3 should contain more users that the first threshold.
        for i in range(11):
            UserFactory(email=f"user{i}@trusted_3.test", date_joined=today)
            UserFactory(email=f"user{i}@not_trusted_3.test", date_joined=today)

        self.expected_msg_domain2 = (
            "10 accounts use the trusted domain '@trusted_2.test' - "
            "the day before it was 0 (threshold exceeded: 10)"
        )

        self.expected_msg_domain3 = (
            "11 accounts use the trusted domain '@trusted_3.test' - "
            "the day before it was 0 (threshold exceeded: 10)"
        )

    @MockNow.Context()
    @patch("core.management.commands.watch_account_number.write_in_channel")
    def test_command_without_arg(self, write_in_channel_mock):
        """
        Without any argument the command should count the accounts created
        today, and send alerts on Discord.
        """
        out = StringIO()
        call_command("watch_account_number", stdout=out)
        output = out.getvalue()
        self.assertNotIn("trusted_1.test", output)
        self.assertIn(self.expected_msg_domain2, output)
        self.assertIn(self.expected_msg_domain3, output)
        self.assertEqual(write_in_channel_mock.call_count, 3)

    @MockNow.Context()
    @patch("core.management.commands.watch_account_number.write_in_channel")
    def test_message_are_not_sent_on_discord_when_asked(self, write_in_channel_mock):
        """
        No alert is sent with --stdout-only.
        """
        out = StringIO()
        call_command("watch_account_number", stdout_only=True, stdout=out)
        output = out.getvalue()
        self.assertNotIn("trusted_1.test", output)
        self.assertIn(self.expected_msg_domain2, output)
        self.assertIn(self.expected_msg_domain3, output)
        self.assertEqual(write_in_channel_mock.call_count, 0)

    @MockNow.Context()
    @patch("core.management.commands.watch_account_number.write_in_channel", new=lambda x, y: True)
    def test_specific_date_can_be_targeted(self):
        """
        A specific date can be targeted with --date.
        """
        out = StringIO()

        somewhere_tomorrow = timezone.now() + timedelta(days=1, hours=1)
        UserFactory(email=f"user10@trusted_1.test", date_joined=somewhere_tomorrow)

        call_command("watch_account_number", date=somewhere_tomorrow.date(), stdout=out)
        output = out.getvalue()

        self.assertIn(
            "10 accounts use the trusted domain '@trusted_1.test' - "
            "the day before it was 9 (threshold exceeded: 10)",
            output,
        )
        self.assertNotIn(self.expected_msg_domain2, output)
        self.assertNotIn(self.expected_msg_domain3, output)
