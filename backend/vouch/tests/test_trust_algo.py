"""
All test cases of the trust algorithm.
"""

import numpy as np
from django.test import TestCase

from core.models import user
from core.models.user import EmailDomain
from core.tests.factories.user import UserFactory
from vouch.models import Voucher
from vouch.trust_algo import (
    MIN_PRETRUST_VOTING_RIGHT,
    PRETRUST_BIAS,
    compute_relative_posttrusts,
    compute_voting_rights,
    normalize_vouch_matrix,
    trust_algo,
)

EPSILON = 0.0000001


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
        """
        The normalized vouch matrix must be row-stochastic, i.e. each
        voucher's total vouch must equal 1.
        """
        vouch_matrix = np.random.rand(self._nb_users, self._nb_users)
        user_trusts = np.random.randint(2, size=self._nb_users)
        normalized_vouch_matrix = normalize_vouch_matrix(vouch_matrix, user_trusts)
        for u in range(self._nb_users):
            self.assertAlmostEqual(np.sum(normalized_vouch_matrix[u]), 1)

    def test_compute_relative_posttrusts(self):
        """
        The sum of relative post trusts must equal 1. Posttrusts must also
        assign at least `PRETRUST_BIAS` to pretrusted users. Finally, it
        should assign a zero trust to non-pretrusted non-vouched users.
        """
        vouch_matrix = np.random.rand(self._nb_users, self._nb_users)
        pretrusts = np.random.randint(2, size=self._nb_users)
        relative_pretrusts = pretrusts / np.sum(pretrusts)
        normalized_vouch_matrix = normalize_vouch_matrix(vouch_matrix, pretrusts)
        relative_posttrusts = compute_relative_posttrusts(
            normalized_vouch_matrix, relative_pretrusts
        )

        # ensure it sums to 1
        self.assertAlmostEqual(np.sum(relative_posttrusts), 1)
        # ensure sum_trusted >= PRETRUST_BIAS
        self.assertTrue(
            np.sum(
                [
                    relative_posttrusts[u]
                    for u in range(len(relative_posttrusts))
                    if pretrusts[u] > 0
                ]
            )
            >= PRETRUST_BIAS
        )
        # ensure that all pretrusted users have a positive relative posttrust
        for relative_posttrust, pretrust in zip(relative_posttrusts, pretrusts):
            if pretrust > 0:
                self.assertTrue(relative_posttrust > 0)

        # ensure that untrusted users than aren't vouched for don't get trust
        untrusted_user = self._nb_users - 1
        pretrusts[untrusted_user] = 0
        vouch_matrix[:, untrusted_user] = 0
        relative_pretrusts = pretrusts / np.sum(pretrusts)
        normalized_vouch_matrix = normalize_vouch_matrix(vouch_matrix, pretrusts)
        relative_posttrusts = compute_relative_posttrusts(
            normalized_vouch_matrix, relative_pretrusts
        )
        self.assertAlmostEqual(relative_posttrusts[untrusted_user], 0)

    def test_compute_voting_rights(self):
        """
        The voting rights of pretrusted users must be at least
        `MIN_PRETRUST_VOTING_RIGHT`. Moreover, unless the voting right is
        clipped to 1, it must be proportional to posttrust.
        """
        pretrusts = np.random.randint(2, size=self._nb_users)
        posttrusts = np.random.randint(20, 100, self._nb_users)
        for u in range(len(pretrusts)):
            if pretrusts[u] == 0 and np.random.rand() < 0.5:
                posttrusts[u] = 0
        relative_posttrusts = posttrusts / np.sum(posttrusts)
        min_idx = np.argmin(
            [
                relative_posttrusts[u] if pretrusts[u] == 1 else float("inf")
                for u in range(self._nb_users)
            ]
        )
        scale_fac = relative_posttrusts[min_idx] / MIN_PRETRUST_VOTING_RIGHT
        voting_rights = compute_voting_rights(relative_posttrusts, pretrusts)

        self.assertAlmostEqual(voting_rights[min_idx], MIN_PRETRUST_VOTING_RIGHT)
        for u in range(self._nb_users):
            self.assertTrue(voting_rights[u] >= -EPSILON)
            self.assertTrue(voting_rights[u] <= 1 + EPSILON)
            self.assertTrue(
                voting_rights[u] * scale_fac <= relative_posttrusts[u] + EPSILON
            )
            if voting_rights[u] < 1 - EPSILON:
                self.assertAlmostEqual(
                    voting_rights[u], relative_posttrusts[u] / scale_fac
                )
            if pretrusts[u] > 0:
                self.assertTrue(voting_rights[u] >= MIN_PRETRUST_VOTING_RIGHT - EPSILON)

    def test_trust_algo(self):
        users = list(user.User.objects.all())
        for u in users:
            self.assertIsNone(u.trust_score)
        trust_algo()
        users = list(user.User.objects.all())
        self.assertTrue(users[1].trust_score >= MIN_PRETRUST_VOTING_RIGHT - EPSILON)
        self.assertTrue(users[2].trust_score > EPSILON)
        self.assertAlmostEqual(users[9].trust_score, 0)
        self.assertAlmostEqual(users[8].trust_score, 0)
        vouch18 = Voucher(by=self.user_1, to=self.user_8, trust_value=100.0)
        vouch18.save()
        trust_algo()
        users = list(user.User.objects.all())
        self.assertTrue(users[8].trust_score > EPSILON)
