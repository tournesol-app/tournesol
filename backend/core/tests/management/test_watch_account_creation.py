from io import StringIO
from unittest import mock

from django.core.management import call_command
from django.test import TestCase

from core.models.user import EmailDomain
from core.tests.factories.user import UserFactory
from core.utils.time import time_ago


class WatchAccountCreationTestCase(TestCase):

    @mock.patch("core.lib.discord.api.write_in_channel")
    def test_cmd_watch_account_creation(self, write_in_channel_mock):
        
        out = StringIO()

        EmailDomain.objects.create(domain="@verified.test", status=EmailDomain.STATUS_ACCEPTED)
        UserFactory(email="user1@verified.test", date_joined=time_ago(minutes=5))

        call_command("watch_account_creation", since-n-hours=1, n-accounts=1, stdout=out)
        output = out.getvalue()
        
        self.assertIn("1 accounts were created during the last 1 hour(s) "
                      "with the domain '@verified.test'", output)
        
        self.assertIn("success", output)

        self.assertEqual(write_in_channel_mock.call_count, 1)
  