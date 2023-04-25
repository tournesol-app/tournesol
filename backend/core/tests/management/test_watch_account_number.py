from datetime import timedelta
from io import StringIO
from unittest import mock

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from core.models.user import EmailDomain
from core.tests.factories.user import UserFactory


class WatchAccountNumberTestCase(TestCase):
    def setUp(self):
        today = timezone.now().date()
    # Creates 6 domains : 3 trusted and 3 not-trusted with 9, 10 and 11 users.
        for n in range(3):
            EmailDomain.objects.create(domain=f"@trusted{n}.test", status=EmailDomain.STATUS_ACCEPTED)
            EmailDomain.objects.create(domain=f"@not-trusted{n}.test", status=EmailDomain.STATUS_REJECTED)
            for i in range(9+n):
                UserFactory(email=f"user{i}@trusted{n}.test", date_joined=today)
                UserFactory(email=f"user{i}@not-trusted{n}.test", date_joined=today)

    @mock.patch("core.lib.discord.api.write_in_channel")
    def test_discord_alerts(self, write_in_channel_mock):

        out = StringIO()

        call_command("watch_account_number", date=timezone.now().date(), stdout=out)
        output = out.getvalue()
        
        self.assertIn("11 accounts use the trusted domain '@trusted2.test' - the day before it was 0 (threshold exceeded: 10)", output)
        self.assertIn("10 accounts use the trusted domain '@trusted1.test' - the day before it was 0 (threshold exceeded: 10)", output)
        self.assertEqual(write_in_channel_mock.call_count, 2)

    @mock.patch("core.lib.discord.api.write_in_channel")
    def test_stdout_only(self, write_in_channel_mock):
        
        out = StringIO()

        call_command("watch_account_number", date=timezone.now().date(), stdout_only=True, stdout=out)
        output = out.getvalue()
        
        self.assertIn("11 accounts use the trusted domain '@trusted2.test' - the day before it was 0 (threshold exceeded: 10)", output)
        self.assertIn("10 accounts use the trusted domain '@trusted1.test' - the day before it was 0 (threshold exceeded: 10)", output)
        self.assertEqual(write_in_channel_mock.call_count, 0)

    def test_date_arg(self):
        
        out = StringIO()
        tomorrow = (timezone.now() + timedelta(days=1)).date()

        UserFactory(email=f"user10@trusted0.test", date_joined=tomorrow)

        call_command("watch_account_number", date=tomorrow, stdout=out)
        output = out.getvalue()

        self.assertNotIn("10 accounts use the trusted domain '@trusted1.test' - the day before it was 0 (threshold exceeded: 10)", output)
        self.assertIn("10 accounts use the trusted domain '@trusted0.test' - the day before it was 9 (threshold exceeded: 10)", output)
        