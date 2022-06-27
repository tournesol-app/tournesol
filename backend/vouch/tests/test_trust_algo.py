"""
All test cases of the trust algorithm.
"""

import numpy as np
from django.test import TestCase

from core.models import user
from core.models.user import EmailDomain
from core.tests.factories.user import UserFactory
from vouch.models import Voucher
from vouch.trust_algo import normalize_vouch_matrix, compute_relative_posttrust, compute_voting_rights, trust_algo, PRETRUST_BIAS


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

    def test_normalize_vouch_matrix(self):
        vouch_matrix = np.random.rand(self._nb_users, self._nb_users)
        user_trust = np.random.randint(2, size=self._nb_users)
        normalized_vouch_matrix = normalize_vouch_matrix(vouch_matrix, user_trust)
        for user in range(self._nb_users):
            self.assertAlmostEqual(np.sum(normalized_vouch_matrix[user]), 1)

    def test_compute_relative_posttrust(self):
        vouch_matrix = np.random.rand(self._nb_users, self._nb_users)
        pretrust = np.random.randint(2, size=self._nb_users)
        relative_pretrust = pretrust/np.sum(pretrust)
        normalized_vouch_matrix = normalize_vouch_matrix(vouch_matrix, pretrust)
        relative_posttrust = compute_relative_posttrust(normalized_vouch_matrix, relative_pretrust)

        # ensure it sums to 1
        self.assertAlmostEqual(np.sum(relative_posttrust), 1)
        # ensure sum_trusted >= PRETRUST_BIAS
        self.assertTrue(
            np.sum([relative_posttrust[user] for user in range(len(relative_posttrust)) if pretrust[user] > 0]) >= PRETRUST_BIAS
        )
        # ensure that untrusted users than aren't vouched for don't get trust
        untrusted_user = self._nb_users - 1
        pretrust[untrusted_user] = 0
        vouch_matrix[:, untrusted_user] = 0
        relative_pretrust = pretrust/np.sum(pretrust)
        normalized_vouch_matrix = normalize_vouch_matrix(vouch_matrix, pretrust)
        relative_posttrust = compute_relative_posttrust(normalized_vouch_matrix, relative_pretrust)
        self.assertAlmostEqual(relative_posttrust[untrusted_user], 0)

    def test_compute_voting_rights(self):
        posttrust = np.random.randint(0, 100, self._nb_users)
        relative_posttrust = posttrust/np.sum(posttrust)
        pretrust = np.random.randint(2, size=self._nb_users)
        min_idx = np.argmin(
            [relative_posttrust[user] if pretrust[user] == 1 else float('inf') for user in range(self._nb_users)]
        )
        scale_fac = relative_posttrust[min_idx]
        voting_rights = compute_voting_rights(relative_posttrust, pretrust)
        
        self.assertAlmostEqual(voting_rights[min_idx], 1)
        for user in range(self._nb_users):
            self.assertAlmostEqual(voting_rights[user] * scale_fac, relative_posttrust[user])
            if pretrust[user] > 0:
                self.assertTrue(voting_rights[user] >= 0.999999999)

    def test_trust_algo(self):
        users = list(user.User.objects.all())
        for u in users:
            self.assertIsNone(u.trust_score)
        trust_algo()
        users = list(user.User.objects.all())
        self.assertTrue(users[1].trust_score >= 0.9999999)
        self.assertTrue(users[2].trust_score > 0.00001)
        self.assertAlmostEqual(users[9].trust_score, 0)
        self.assertAlmostEqual(users[8].trust_score, 0)
        vouch18 = Voucher(by=self.user_1, to=self.user_8, trust_value=100.0)
        vouch18.save()
        trust_algo()
        users = list(user.User.objects.all())
        self.assertTrue(users[8].trust_score > 0.00001)
