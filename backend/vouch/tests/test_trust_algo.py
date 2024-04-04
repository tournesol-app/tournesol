"""
All test cases of the trust algorithm.
"""
from django.test import TestCase

from core.models.user import EmailDomain, User
from core.tests.factories.user import UserFactory
from vouch.models import Voucher
from vouch.trust_algo import TRUSTED_EMAIL_PRETRUST, trust_algo


class TrustAlgoTest(TestCase):
    _user_0 = "username_0"
    _user_1 = "username_1"
    _user_2 = "username_2"
    _user_3 = "username_3"
    _user_4 = "username_4"
    _user_5 = "username_5"
    _user_6 = "username_6"
    _user_7 = "username_7"
    _user_8 = "username_8"
    _user_9 = "username_9"
    _nb_users = 10

    def setUp(self) -> None:
        self.user_0 = UserFactory(username=self._user_0)
        self.user_1 = UserFactory(username=self._user_1, email="user1@trusted.test")
        self.user_2 = UserFactory(username=self._user_2)
        self.user_3 = UserFactory(username=self._user_3, email="user3@trusted.test")
        self.user_4 = UserFactory(username=self._user_4)
        self.user_5 = UserFactory(username=self._user_5)
        self.user_6 = UserFactory(username=self._user_6, email="user6@trusted.test")
        self.user_7 = UserFactory(username=self._user_7)
        self.user_8 = UserFactory(username=self._user_8)
        self.user_9 = UserFactory(username=self._user_9)

        email_domain = EmailDomain.objects.get(domain="@trusted.test")
        email_domain.status = EmailDomain.STATUS_ACCEPTED
        email_domain.save()

        Voucher.objects.bulk_create(
            [
                # user_0 has given zero voucher
                # user_1 has given three vouchers
                Voucher(by=self.user_1, to=self.user_0),
                Voucher(by=self.user_1, to=self.user_3),
                Voucher(by=self.user_1, to=self.user_7),
                # user_2 has given one voucher
                Voucher(by=self.user_2, to=self.user_5),
                # user_3 has given two vouchers
                Voucher(by=self.user_3, to=self.user_1),
                Voucher(by=self.user_3, to=self.user_5),
                # user_4 has given one voucher
                Voucher(by=self.user_4, to=self.user_7),
                # user_5 has given one voucher
                Voucher(by=self.user_5, to=self.user_1),
                # user_6 has given zero voucher
                # user_7 has given two vouchers
                Voucher(by=self.user_7, to=self.user_1),
                Voucher(by=self.user_7, to=self.user_2),
                # user_8 has given one voucher
                Voucher(by=self.user_8, to=self.user_3),
                # user_9 has given two vouchers
                Voucher(by=self.user_9, to=self.user_4),
                Voucher(by=self.user_9, to=self.user_5),
            ]
        )

    def test_trust_algo(self):
        users = list(User.objects.all())
        for user in users:
            self.assertIsNone(user.trust_score)

        trust_algo()
        users = list(User.objects.all().order_by('username'))
        self.assertTrue(users[1].trust_score >= TRUSTED_EMAIL_PRETRUST)
        self.assertTrue(users[2].trust_score > 0)
        self.assertAlmostEqual(users[9].trust_score, 0)
        self.assertAlmostEqual(users[8].trust_score, 0)

        vouch18 = Voucher(by=self.user_1, to=self.user_8)
        vouch18.save()
        trust_algo()
        users = list(User.objects.all().order_by('username'))
        self.assertTrue(users[8].trust_score > 0)

    def test_trust_algo_without_pretrusted_users_is_noop(self):
        # Keep only users without trusted emails
        User.objects.exclude(
            username__in=[self._user_7, self._user_8, self._user_9]
        ).delete()

        for user in User.objects.all():
            self.assertIsNone(user.trust_score)
        trust_algo()
        for user in User.objects.all():
            self.assertIsNone(user.trust_score)

    def test_trust_algo_without_voucher(self):
        Voucher.objects.all().delete()

        for user in User.objects.all():
            self.assertIsNone(user.trust_score)

        trust_algo()

        for user in User.objects.all():
            if user.has_trusted_email:
                self.assertEqual(user.trust_score, TRUSTED_EMAIL_PRETRUST)
            else:
                self.assertEqual(user.trust_score, 0.0)

    def test_trust_algo_db_requests_count(self):
        with self.assertNumQueries(3):
            trust_algo()
