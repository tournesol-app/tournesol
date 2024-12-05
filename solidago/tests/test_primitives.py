import pytest
import numpy as np

from solidago.primitives import (
    qr_quantile,
    qr_median,
    qr_standard_deviation,
    lipschitz_resilient_mean,
)


def test_qrmedian_resilience():
    median = qr_median(
        lipschitz=1.0,
        voting_rights=1.0,
        values=np.array([-10.0, 5.0, 10.0]),
        left_uncertainties=np.array([1e-3, 1e-7, 1e-3]),
        right_uncertainties=np.array([1e-5, 1e-3, 1e-4]),
    )
    assert median == pytest.approx(1.0, abs=1e-3)


def test_qrmed_with_high_uncertainty():
    """Each score with a high uncertainty will have less effect on QrMed."""
    median = qr_median(
        lipschitz=1.0,
        voting_rights=1.0,
        values=np.array([-10.0, 1.0, 10.0]),
        left_uncertainties=np.array([1e6]*3),
    )
    assert median == pytest.approx(0.0, abs=1e-5)


def test_qr_quantile_zero_uncertainty_correct_prior():
    quantile = qr_quantile(
        lipschitz=0.1,
        quantile=0.25,
        voting_rights=1.0,
        values=np.array([0.0, 1.0, 2.0, 5.0]),
        left_uncertainties=np.array([1e-6] * 4),
        right_uncertainties=np.array([1e-4] * 4),
        default_value=1.0,
        error=1e-5,
    )
    assert quantile == pytest.approx(1, abs=1e-3)


def test_qr_quantile_zero_uncertainty_incorrect_prior():
    quantile = qr_quantile(
        lipschitz=1e9,
        quantile=0.21,
        voting_rights=1.0,
        values=np.array([0.0, 1.0, 2.0, 6.0, 9.0, 5.0, 3.0, 5.0, 4.0, 7.0]),
        left_uncertainties=np.array([1e-6] * 10),
        right_uncertainties=np.array([1e-4] * 10),
        default_value=0.0,
        error=1e-5,
    )
    assert quantile == pytest.approx(2, abs=1e-3)


def test_qr_quantile_high_uncertainty():
    quantile = qr_quantile(
        lipschitz=1.0,
        quantile=0.5,
        voting_rights=1.0,
        values=np.array([1.0, 2.0, 6.0, 9.0]),
        left_uncertainties=np.array([1e8] * 4),
        right_uncertainties=np.array([1e9] * 4),
        default_value=0.0,
        error=1e-5,
    )
    assert quantile == pytest.approx(0, abs=1e-1)


@pytest.mark.parametrize(
    "lipshitz,w,x,delta,quantile,expected_result",
    [
        (0.1, np.array([0.1]), np.array([0.]), np.array([0.1]), 0.5, 0),
        (0.1, np.array([0.1]), np.array([0.]), np.array([0.1]), 0.1, 0),
        (0.1, np.array([0.1]), np.array([0.]), np.array([0.1]), 0.9, 0),
        (0.1, np.array([1.] * 1000), np.array([-1.] * 500 + [1.] * 500), np.array([0.1] * 1000), 0.10, -0.986816),
        (0.1, np.array([1.] * 1000), np.array([-1.] * 100 + [1.] * 900), np.array([1e-6] * 1000), 0.10, 0.),
        (10000., np.array([1.] * 1000), np.array([-1.] * 102 + [1.] * 898), np.array([1e-6] * 1000), 0.01, -1.),
        (1e12, np.array([1000.] * 1000), np.arange(1000., 2000, 1), np.array([1e-6] * 1000), 0.90, 1899.1817),
    ]
)
def test_qr_quantile_returns_expected_results(lipshitz,w,x,delta,quantile,expected_result):
    assert (
        qr_quantile(
            lipschitz=lipshitz,
            voting_rights=w,
            values=x,
            left_uncertainties=delta,
            quantile=quantile,
        )
        == pytest.approx(expected_result, abs=1e-4)
    )


def test_qr_standard_deviation():
    standard_deviation = qr_standard_deviation(
        lipschitz=1.0,
        values=np.array([-4.0, -2.0, 0.0, 2.0, 4.0]),
        quantile_dev=0.5,
    )
    assert standard_deviation == pytest.approx(2, abs=1e-3)


def test_qr_standard_dev_default():
    default_deviation = 3.0
    dev = qr_standard_deviation(
        lipschitz=0.5,
        default_dev=default_deviation,
        voting_rights=1.0,
        values=np.array([]),
        left_uncertainties=np.array([]),
    )
    assert dev == pytest.approx(default_deviation, abs=1e-5)


def test_qr_standard_dev_with_high_weight():
    x = np.array([-6.0, 0.0, 15.0])
    dev = qr_standard_deviation(
        lipschitz=0.5,
        default_dev=1.0,
        voting_rights=1e5,
        values=x,
    )
    assert dev == pytest.approx(np.median(np.abs(x)), abs=1e-5)


def test_lipschitz_resilient_mean():
    values = np.random.normal(0, 1, 20)
    mean = lipschitz_resilient_mean(
        lipschitz=1e3,
        voting_rights=1.0,
        values=values,
        left_uncertainties=np.array([1e-6] * 20),
        right_uncertainties=np.array([1e-4] * 20),
        default_value=0.0,
        error=1e-5,
    )
    assert mean == pytest.approx(values.mean(), abs=1e-3)
