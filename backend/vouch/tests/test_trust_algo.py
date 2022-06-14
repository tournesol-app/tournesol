"""
All test cases of the trust algorithm.
"""

import numpy as np
import pytest
from django.test import TestCase

from core.models import user
from core.models.user import EmailDomain
from core.tests.factories.user import UserFactory
from vouch.models import Voucher
from vouch.trust_algo import get_trust_vector, normalize_trust_values, rescale, trust_algo


class TrustAlgoTestCse(TestCase):
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
                Voucher(by=self.user_1, to=self.user_0, trust_value=10),
                Voucher(by=self.user_1, to=self.user_3, trust_value=13),
                Voucher(by=self.user_1, to=self.user_7, trust_value=17),
                # user_2 has given one voucher
                Voucher(by=self.user_2, to=self.user_5, trust_value=15),
                # user_3 has given two vouchers
                Voucher(by=self.user_3, to=self.user_1, trust_value=31),
                Voucher(by=self.user_3, to=self.user_5, trust_value=35),
                # user_4 has given one voucher
                Voucher(by=self.user_4, to=self.user_7, trust_value=47),
                # user_5 has given one voucher
                Voucher(by=self.user_5, to=self.user_1, trust_value=51),
                # user_6 has given zero voucher
                # user_7 has given two vouchers
                Voucher(by=self.user_7, to=self.user_1, trust_value=71),
                Voucher(by=self.user_7, to=self.user_2, trust_value=72),
                # user_8 has given one voucher
                Voucher(by=self.user_8, to=self.user_3, trust_value=83),
                # user_9 has given two vouchers
                Voucher(by=self.user_9, to=self.user_4, trust_value=94),
                Voucher(by=self.user_9, to=self.user_5, trust_value=95),
            ]
        )

    def test_normalization(self):
        C = np.random.rand(10, 10)
        user_trust = np.random.randint(2, size=10)
        C_normalized = normalize_trust_values(C, user_trust)
        for k in range(len(C_normalized[0])):
            assert np.sum(C_normalized[k]) == pytest.approx(1, 0.00000001)

    def test_get_trust_vector(self):
        # compute trust vector given C and p
        C = np.random.rand(10, 10)
        p = np.random.randint(2, size=10)
        p = p/np.sum(p)
        C_normalized = normalize_trust_values(C, p)
        trust_vec = get_trust_vector(C_normalized, p)

        # ensure it sums to 1
        assert np.sum(trust_vec) == pytest.approx(1, 0.00000001)
        # ensure sum_trusted >= a
        assert np.sum([trust_vec[i] for i in range(len(trust_vec)) if p[i] > 0]) >= 0.2
        # ensure that untrusted users than aren't vouched for don't get trust
        p[9] = 0
        C[:, 9] = 0
        p = p/np.sum(p)
        C_normalized = normalize_trust_values(C, p)
        trust_vec = get_trust_vector(C_normalized, p)
        assert trust_vec[9] == pytest.approx(0, 0.00000001)

    def test_rescale(self):
        trust_vect = np.random.randint(0, 100, 10)
        trust_vect = trust_vect/np.sum(trust_vect)
        trust_stat = np.random.randint(0, 2, 10)
        min_idx = 100
        min_idx = np.argmin([trust_vect[i] if trust_stat[i] ==
                            1 else 2 for i in range(len(trust_vect))])
        scale_fac = trust_vect[min_idx]
        rescaled = rescale(trust_vect, trust_stat)
        assert rescaled[min_idx] == pytest.approx(1, 0.00000001)
        for i in range(len(trust_stat)):
            assert rescaled[i] * scale_fac == pytest.approx(trust_vect[i], 0.00000001)

            if trust_stat[i] > 0:
                assert rescaled[i] >= 0.999999999

    def test_trust_algo(self):
        users = list(user.User.objects.all())
        for u in users:
            self.assertIsNone(u.trust_score)
        trust_algo()
        users = list(user.User.objects.all())
        assert users[1].trust_score >= 0.9999999
        assert users[2].trust_score > 0.00001
        assert users[9].trust_score == pytest.approx(0, 0.00000001)
        assert users[8].trust_score == pytest.approx(0, 0.00000001)
        vouch18 = Voucher(by=self.user_1, to=self.user_8, trust_value=100.0)
        vouch18.save()
        trust_algo()
        users = list(user.User.objects.all())
        assert users[8].trust_score > 0.00001
