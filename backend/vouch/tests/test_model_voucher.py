"""
All test cases of the `Voucher` model.
"""

from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase

from core.tests.factories.user import UserFactory
from vouch.models import Voucher


class VoucherTestCase(TestCase):
    """
    TestCase of the `Voucher` model.
    """

    # For convenience this _user_0 should neither give nor receive any
    # voucher.
    _user_0 = "username_0"
    _user_1 = "username_1"
    _user_2 = "username_2"
    _user_3 = "username_3"
    _user_4 = "username_4"

    def setUp(self):
        self.user_0 = UserFactory(username=self._user_0)
        self.user_1 = UserFactory(username=self._user_1)
        self.user_2 = UserFactory(username=self._user_2)
        self.user_3 = UserFactory(username=self._user_3)
        self.user_4 = UserFactory(username=self._user_4)

        Voucher.objects.bulk_create(
            [
                # user_1 has given one voucher
                Voucher(by=self.user_1, to=self.user_2, value=12),
                # user_2 has given two vouchers
                Voucher(by=self.user_2, to=self.user_1, value=21),
                Voucher(by=self.user_2, to=self.user_3, value=23),
                # user_3 has given three vouchers
                Voucher(by=self.user_3, to=self.user_1, value=31),
                Voucher(by=self.user_3, to=self.user_2, value=32),
                Voucher(by=self.user_3, to=self.user_4, value=34),
                # user_0 has given / received zero voucher
            ]
        )

    def test_clean(self):
        """
        Test the `clean` method of the model.
        """

        voucher = Voucher(by=self.user_1, to=self.user_1)

        # A user cannot vouch for him/herself.
        with self.assertRaises(ValidationError):
            voucher.clean()

    def test_get_given_to_with_one(self):
        """
        Test `get_given_to` returns the expected voucher when a user has only
        one voucher.
        """
        vouchers, exists = Voucher.get_given_to(self.user_3)
        self.assertEqual(vouchers.count(), 1)
        self.assertEqual(vouchers[0].value, 23)
        self.assertEqual(vouchers[0].by, self.user_2)
        self.assertEqual(vouchers[0].to, self.user_3)
        self.assertEqual(exists, True)

    def test_get_given_to_with_several(self):
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
            self.assertIn(voucher.value, [12, 32])

    def test_get_given_to_with_zero(self):
        """
        Test `get_given_to` returns no voucher when a user has no voucher.
        """
        vouchers, exists = Voucher.get_given_to(self.user_0)
        self.assertEqual(vouchers.count(), 0)
        self.assertEqual(exists, False)

    def test_get_given_by_with_one(self):
        """
        Test `get_given_by` returns the expected voucher when a user has given
        only one voucher.
        """
        vouchers, exists = Voucher.get_given_by(self.user_1)
        self.assertEqual(vouchers.count(), 1)
        self.assertEqual(vouchers[0].value, 12)
        self.assertEqual(vouchers[0].by, self.user_1)
        self.assertEqual(vouchers[0].to, self.user_2)
        self.assertEqual(exists, True)

    def test_get_given_by_with_several(self):
        """
        Test `get_given_by` returns only the expected vouchers when a user has
        given several vouchers.
        """
        vouchers, exists = Voucher.get_given_by(self.user_3)
        self.assertEqual(vouchers.count(), 3)
        self.assertEqual(exists, True)

        # Even if the order of the returned vouches is not known, check if
        # their values are expected.
        for voucher in vouchers:
            self.assertEqual(voucher.by, self.user_3)
            self.assertIn(voucher.to, [self.user_1, self.user_2, self.user_4])
            self.assertIn(voucher.value, [31, 32, 34])

    def test_get_given_by_with_zero(self):
        """
        Test `get_given_by` returns no voucher when a user has given no
        voucher.
        """
        vouchers, exists = Voucher.get_given_by(self.user_0)
        self.assertEqual(vouchers.count(), 0)
        self.assertEqual(exists, False)

    def test_user_cant_vouch_twice_for_the_same_target(self):
        """
        Only one voucher can be created for the couple `by` and `to`.
        """
        duplicate = Voucher(by=self.user_1, to=self.user_2, value=13)
        with self.assertRaises(ValidationError):
            duplicate.full_clean()
        with self.assertRaises(IntegrityError):
            duplicate.save()
