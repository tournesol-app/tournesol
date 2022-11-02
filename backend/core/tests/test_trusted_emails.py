from django.test import TestCase

from core.models import EmailDomain, User


class TestTrustedEmails(TestCase):
    def test_user_trusted_based_on_email_domain(self):
        user = User.objects.create_user(username="test-user", email="test@example.test")
        email_domain = EmailDomain.objects.filter(domain="@example.test").first()
        self.assertIsNotNone(email_domain)
        self.assertFalse(user.has_trusted_email)

        email_domain.status = EmailDomain.STATUS_ACCEPTED
        email_domain.save()
        self.assertTrue(user.has_trusted_email)

    def test_queryset_with_trusted_email(self):
        user1 = User.objects.create_user(username="user1", email="test@trusted.test")
        EmailDomain.objects.filter(domain="@trusted.test").update(status=EmailDomain.STATUS_ACCEPTED)
        user2 = User.objects.create_user(username="user2", email="test@untrusted.test")

        self.assertEqual(User.objects.count(), 2)
        users_with_trusted_email = User.with_trusted_email()
        self.assertEqual(users_with_trusted_email.count(), 1)
        self.assertEqual(list(users_with_trusted_email.values_list("username", flat=True)), ["user1"])
