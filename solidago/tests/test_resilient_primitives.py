from unittest import TestCase

import numpy as np

from solidago.resilient_primitives import QrDev, QrMed, QrUnc


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
            0.5,  # influence of the median contributor is bounded by weight / W
            places=3,
        )

    def test_qrmed_with_W_equals_zero(self):
        """Setting W to 0 is like removing the bias towards 0"""
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
            places=3,
        )

    def test_qrmed_with_high_uncertainty(self):
        """Each score with a high uncertainty will have less effect on QrMed."""
        self.assertAlmostEqual(
            QrMed(
                W=1.0,
                w=1.0,
                x=np.array([-10.0, 1.0, 10.0]),
                delta=1000000.0,
            ),
            0.0,
            places=5,
        )


class QrDevTest(TestCase):
    def test_qrdev_default(self):
        default_deviation = 3.0
        self.assertEqual(
            QrDev(
                W=2.0,
                default_dev=default_deviation,
                w=1.0,
                x=np.array([]),
                delta=np.array([]),
            ),
            default_deviation,
        )

    def test_qrdev_with_high_weight(self):
        x = np.array([-6.0, 0.0, 15.0])
        self.assertAlmostEqual(
            QrDev(
                W=2.0,
                default_dev=1.0,
                w=100000.0,
                x=x,
                delta=0.0,
            ),
            float(np.median(np.abs(x))),  # = 6.
            places=5,
        )

    def test_qrdev_with_W_equals_0(self):
        """Setting W to 0 is like removing the bias towards default_dev"""
        x = np.array([-6.0, 0.0, 15.0])
        self.assertAlmostEqual(
            QrDev(
                W=0.0,
                default_dev=1.0,
                w=1.0,
                x=x,
                delta=0.0,
            ),
            float(np.median(np.abs(x))),  # = 6.
            places=5,
        )

    def test_qrdev_with_high_uncertainty(self):
        """
        Each score with a high uncertainty will have less
        effect on QrMed, and thus also on QrDev, which will
        thus not change much from its default deviation.
        """
        default_deviation = 3
        x = np.array([-6.0, 0.0, 15.0])
        self.assertAlmostEqual(
            QrDev(
                W=2.0,
                default_dev=default_deviation,
                w=1.0,
                x=x,
                delta=100000000.0,
            ),
            default_deviation,
            places=5,
        )


class QrUncTest(TestCase):
    def test_qrunc(self):
        W = 2
        weight = 1
        self.assertAlmostEqual(
            QrUnc(
                W,
                default_dev=1,
                w=weight,
                x=np.array([-10.0, 1.0, 10.0]),
                delta=np.array([1e-3, 1e-3, 1e-3]),
            ),
            1.0,
            places=3,
        )

    def test_qrunc_with_W_equals_zero(self):
        W = 0
        weight = 1
        self.assertAlmostEqual(
            QrUnc(
                W,
                default_dev=1,
                w=weight,
                x=np.array([-10.0, 1.0, 10.0]),
                delta=np.array([1e-3, 1e-3, 1e-3]),
            ),
            0.02,
            places=2,
        )
