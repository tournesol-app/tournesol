"""
All test cases of the `Voucher` model.
"""

from django.test import TestCase

from core.tests.factories.user import UserFactory
from vouch.models import Voucher


class VoucherTestCase(TestCase):
    """
    TestCase of the `Voucher` model.
    """

    _user_1 = "username_1"
    _user_2 = "username_2"
    _user_3 = "username_3"
    _user_4 = "username_4"

    def setUp(self) -> None:
        self.user_1 = UserFactory(username=self._user_1)
        self.user_2 = UserFactory(username=self._user_2)
        self.user_3 = UserFactory(username=self._user_3)
        self.user_4 = UserFactory(username=self._user_4)

        Voucher.objects.bulk_create(
            [
                Voucher(by=self.user_1, to=self.user_2, trust_value=12),
                Voucher(by=self.user_1, to=self.user_4, trust_value=14),
                Voucher(by=self.user_3, to=self.user_1, trust_value=31),
                Voucher(by=self.user_3, to=self.user_2, trust_value=32),
                Voucher(by=self.user_3, to=self.user_4, trust_value=34),
            ]
        )

    def test_get_given_to_with_one(self) -> None:
        """
        Test `get_given_to` returns the expected voucher when a user has only
        one voucher.
        """
        vouchers, exists = Voucher.get_given_to(self.user_1)
        self.assertEqual(vouchers.count(), 1)
        self.assertEqual(vouchers[0].trust_value, 31)
        self.assertEqual(vouchers[0].by, self.user_3)
        self.assertEqual(vouchers[0].to, self.user_1)
        self.assertEqual(exists, True)

    def test_get_given_to_with_several(self) -> None:
        """
        Test `get_given_to` returns only the expected vouchers when a user has
        several vouchers.
        """
        vouchers, exists = Voucher.get_given_to(self.user_2)
        self.assertEqual(vouchers.count(), 2)
        self.assertEqual(exists, True)

        # Even if the order of the returned vouches is not known, check if
        # their values are expected.
        for voucher in vouchers:
            self.assertEqual(voucher.to, self.user_2)
            self.assertIn(voucher.by, [self.user_1, self.user_3])
            self.assertIn(voucher.trust_value, [12, 32])

    def test_get_given_to_with_zero(self) -> None:
        """
        Test `get_given_to` returns no voucher when a user has no voucher.
        """
        vouchers, exists = Voucher.get_given_to(self.user_3)
        self.assertEqual(vouchers.count(), 0)
        self.assertEqual(exists, False)

    def get_received_by(self) -> None:
        pass
