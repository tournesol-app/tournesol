from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from core.models.user import User
from core.tests.factories.user import UserFactory
from core.utils.time import time_ago


class DeleteInactiveUsersTestCase(TestCase):
    default_period = 7

    def test_cmd_delete_old_inactive_users(self):
        out = StringIO()

        old_date = time_ago(days=self.default_period + 1)
        recent_date = time_ago(days=self.default_period - 1)

        # active users must not be deleted
        UserFactory(username="still_there_1", is_active=True, date_joined=old_date)
        UserFactory(username="still_there_2", is_active=True, date_joined=recent_date)

        # only old inactive users must be deleted
        users_to_delete = [
            UserFactory(is_active=False, date_joined=old_date),
            UserFactory(is_active=False, date_joined=old_date),
            UserFactory(is_active=False, date_joined=old_date, last_login=old_date),
        ]
        UserFactory(username="still_there_3", is_active=False, date_joined=recent_date)
        UserFactory(username="still_there_4", is_active=False, date_joined=recent_date)

        # inactive users that have recently been marked as deleted should be preserved
        UserFactory(
            username="still_there_5", is_active=False, date_joined=old_date, last_login=recent_date
        )

        n_users_before = User.objects.count()
        n_users_to_delete = len(users_to_delete)

        call_command("delete_inactive_users", stdout=out)
        output = out.getvalue()
        n_users_after = User.objects.count()

        self.assertIn(f"{n_users_to_delete} users deleted", output)
        self.assertIn("success", output)
        self.assertEqual(n_users_after, n_users_before - n_users_to_delete)

        # check no exception is raised by retrieving the expected users
        for i in range(5):
            User.objects.get(username=f"still_there_{i+1}")

    def test_cmd_verbosity_levels(self):
        # verbosity 1
        out = StringIO()
        call_command("delete_inactive_users", stdout=out)
        output = out.getvalue()
        self.assertNotIn(f"MGMT_DELETE_INACTIVE_USERS_PERIOD: {self.default_period}", output)

        # verbosity 2
        out = StringIO()
        call_command("delete_inactive_users", verbosity=2, stdout=out)
        output = out.getvalue()
        self.assertIn(f"MGMT_DELETE_INACTIVE_USERS_PERIOD: {self.default_period}", output)
        self.assertIn("0 users deleted", output)
        self.assertIn("success", output)
