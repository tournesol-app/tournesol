import pytest
from unittest import TestCase
import numpy as np

from solidago.primitives import (
    qr_quantile, qr_median, qr_standard_deviation, qr_uncertainty, lipschitz_resilient_mean
)


def test_qrmedian_resilience():
    median = qr_median(
        lipschitz=1,
        voting_rights=1,
        values=np.array([-10.0, 5.0, 10.0]),
        left_uncertainties=np.array([1e-3, 1e-7, 1e-3]),
        right_uncertainties=np.array([1e-5, 1e-3, 1e-4]),
    )
    assert median == pytest.approx(1.0, abs=1e-3)

def test_qr_quantile_zero_uncertainty_correct_prior():
    quantile = qr_quantile(
        lipschitz=0.1,
        quantile=0.25,
        voting_rights=1., 
        values=np.array([0., 1., 2., 5.]), 
        left_uncertainties=np.array([1e-6] * 4),
        right_uncertainties=np.array([1e-4] * 4),
        default_value=1.,
        error=1e-5
    )
    assert quantile == pytest.approx(1, abs=1e-3)

def test_qr_quantile_zero_uncertainty_incorrect_prior():
    quantile = qr_quantile(
        lipschitz=1e9,
        quantile=0.21,
        voting_rights=1., 
        values=np.array([0., 1., 2., 6., 9., 5., 3., 5., 4., 7.]), 
        left_uncertainties=np.array([1e-6] * 10),
        right_uncertainties=np.array([1e-4] * 10),
        default_value=0.,
        error=1e-5
    )
    assert quantile == pytest.approx(2, abs=1e-3)
     
def test_qr_quantile_high_uncertainty():
    quantile = qr_quantile(
        lipschitz=1,
        quantile=0.5,
        voting_rights=1., 
        values=np.array([1., 2., 6., 9.]), 
        left_uncertainties=np.array([1e8] * 4),
        right_uncertainties=np.array([1e9] * 4),
        default_value=0.,
        error=1e-5
    )
    assert quantile == pytest.approx(0, abs=1e-1)
    
def test_qr_standard_deviation():
    standard_deviation = qr_standard_deviation(
        lipschitz=1, 
        values=np.array([-4, -2, 0, 2, 4]), 
        quantile_dev=0.5,
    )
    assert standard_deviation == pytest.approx(2, abs=1e-3)

def test_lipschitz_resilient_mean():
    values = np.random.normal(0, 1, 20)
    mean = lipschitz_resilient_mean(
        lipschitz=1e3,
        voting_rights=1., 
        values=values, 
        left_uncertainties=np.array([1e-6] * 20),
        right_uncertainties=np.array([1e-4] * 20),
        default_value=0.,
        error=1e-5
    )
    assert mean == pytest.approx(values.mean(), abs=1e-3)
    
