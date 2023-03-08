from django.test import TestCase

from core.models.user import EmailDomain
from core.tests.factories.user import UserFactory
from core.utils.email_domain import get_email_domain_with_recent_new_users
from core.utils.time import time_ago


class UtilsEmailDomainTestCase(TestCase):
    """TestCase of the utils.email_domain module."""

    def setUp(self):

        EmailDomain.objects.create(domain="@verified.test", status=EmailDomain.STATUS_ACCEPTED)
        EmailDomain.objects.create(domain="@verified2.test", status=EmailDomain.STATUS_ACCEPTED)
        EmailDomain.objects.create(domain="@pending.test", status=EmailDomain.STATUS_PENDING)
        EmailDomain.objects.create(domain="@rejected.test", status=EmailDomain.STATUS_REJECTED)

        UserFactory(email="user1@verified.test", date_joined=time_ago(minutes=5))
        UserFactory(email="user2@verified2.test", date_joined=time_ago(minutes=5))
        UserFactory(email="user3@verified2.test", date_joined=time_ago(minutes=5))
        UserFactory(email="user4@pending.test", date_joined=time_ago(minutes=5))
        UserFactory(email="user5@rejected.test", date_joined=time_ago(minutes=5))

        UserFactory(email="user6@verified.test", date_joined=time_ago(minutes=75))
        UserFactory(email="user7@pending.test", date_joined=time_ago(minutes=75))
        UserFactory(email="user8@pending.test", date_joined=time_ago(minutes=75))
        UserFactory(email="user9@pending.test", date_joined=time_ago(minutes=75))
        UserFactory(email="user10@rejected.test", date_joined=time_ago(minutes=75))

        UserFactory(email="user11@verified.test", date_joined=time_ago(hours=10))
        UserFactory(email="user12@pending.test", date_joined=time_ago(hours=10))
        UserFactory(email="user13@rejected.test", date_joined=time_ago(hours=10))
        UserFactory(email="user14@rejected.test", date_joined=time_ago(days=2))

    def test_get_email_domain_with_recent_new_users(self):
        """Test get user count per email domain at different time"""

        self.assertEqual(len(get_email_domain_with_recent_new_users(time_ago(minutes=1), "ACK", 1)), 0)

        email_accepted_10min = get_email_domain_with_recent_new_users(time_ago(minutes=10), "ACK", 1)
        self.assertEqual(len(email_accepted_10min), 2)
        self.assertEqual(email_accepted_10min[0].domain, "@verified2.test")
        self.assertEqual(email_accepted_10min[0].cnt, 2)
        self.assertEqual(email_accepted_10min[1].domain, "@verified.test")
        self.assertEqual(email_accepted_10min[1].cnt, 1)

        email_accepted_2h = get_email_domain_with_recent_new_users(time_ago(hours=2), "ACK", 2)
        self.assertEqual(email_accepted_2h[0].domain, "@verified.test")
        self.assertEqual(email_accepted_2h[0].cnt, 2)

        email_pending_2h = get_email_domain_with_recent_new_users(time_ago(hours=2), "PD", 3)
        self.assertEqual(email_pending_2h[0].domain, "@pending.test")
        self.assertEqual(email_pending_2h[0].cnt, 4)

        email_rejected_1day = get_email_domain_with_recent_new_users(time_ago(days=1), "RJ", 3)
        self.assertEqual(email_rejected_1day[0].domain, "@rejected.test")
        self.assertEqual(email_rejected_1day[0].cnt, 3)
