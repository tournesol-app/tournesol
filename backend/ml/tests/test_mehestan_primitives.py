import numpy as np
from django.test import TestCase

from ml.mehestan.primitives import QrMed, QrUnc


class QrMedTest(TestCase):
    def test_qrmed(self):
        W = 2
        weight = 1
        self.assertAlmostEqual(
            QrMed(
                W,
                w=weight,
                x=np.array([-10.0, 1.0, 10.0]),
                delta=np.array([1e-3, 1e-3, 1e-3]),
            ),
            0.5, # influence of the median contributor is bounded by weight / W
            places=3
        )

    def test_qrmed_with_W_equals_zero(self):
        W = 0
        weight = 1
        self.assertAlmostEqual(
            QrMed(
                W,
                w=weight,
                x=np.array([-10.0, 1.0, 10.0]),
                delta=np.array([1e-3, 1e-3, 1e-3]),
            ),
            1.0,
            places=3
        )


class QrUncTest(TestCase):
    def test_qrunc(self):
        W = 2
        weight = 1
        self.assertAlmostEqual(
            QrUnc(
                W,
                default_dev=0,
                w=weight,
                x=np.array([-10.0, 1.0, 10.0]),
                delta=np.array([1e-3, 1e-3, 1e-3]),
            ),
            0.506,
            places=3,
        )

    def test_qrunc_with_W_equals_zero(self):
        W = 0
        weight = 1
        self.assertAlmostEqual(
            QrUnc(
                W,
                default_dev=0,
                w=weight,
                x=np.array([-10.0, 1.0, 10.0]),
                delta=np.array([1e-3, 1e-3, 1e-3]),
            ),
            0.033,
            places=3,
        )
