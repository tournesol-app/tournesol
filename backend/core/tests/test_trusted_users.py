from django.test import TestCase

from core.models import User, EmailDomain


class TestTrustedUsers(TestCase):
    def test_user_trusted_based_on_email_domain(self):
        user = User.objects.create_user(username="test-user", email="test@example.test")
        email_domain = EmailDomain.objects.filter(domain="@example.test").first()
        self.assertIsNotNone(email_domain)
        self.assertFalse(user.is_trusted)

        email_domain.status = EmailDomain.STATUS_ACCEPTED
        email_domain.save()
        self.assertTrue(user.is_trusted)

    def test_trusted_users_queryset(self):
        user1 = User.objects.create_user(username="user1", email="test@trusted.test")
        EmailDomain.objects.filter(domain="@trusted.test").update(status=EmailDomain.STATUS_ACCEPTED)
        user2 = User.objects.create_user(username="user2", email="test@untrusted.test")

        self.assertEqual(User.objects.count(), 2)
        trusted_users = User.trusted_users()
        self.assertEqual(trusted_users.count(), 1)
        self.assertEqual(list(trusted_users.values_list("username", flat=True)), ["user1"])
