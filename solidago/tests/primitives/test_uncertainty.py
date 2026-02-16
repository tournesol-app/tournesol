from typing import Any
from numpy.typing import NDArray
from numba import njit

import numpy as np

from solidago.primitives.uncertainty import *


@njit
def prior(values: NDArray, targets: NDArray) -> float:
    return (values**2).sum()

@njit
def nll(values: NDArray, targets: NDArray) -> float:
    return ((values - targets)**2).sum() / 2

prior_cw_loss_getter, nll_cw_loss_getter = to_cw_loss_getter(prior), to_cw_loss_getter(nll) # type: ignore
values, targets = np.zeros(2), np.array([[-1., 0.], [1., 0.]])
eye = np.eye(2)
delta = 1.0

def test_cw_loss_getters():
    cw_prior_loss, args = prior_cw_loss_getter(values, targets)
    assert cw_prior_loss(1.0, np.int64(0), *args) == prior(values + delta * eye[0], targets)
    assert cw_prior_loss(1.0, np.int64(1), *args) == prior(values + delta * eye[1], targets)
    cw_nll, args = nll_cw_loss_getter(values, targets)
    assert cw_nll(1.0, np.int64(0), *args) == nll(values + delta * eye[0], targets)
    assert cw_nll(1.0, np.int64(1), *args) == nll(values + delta * eye[1], targets)
    
cw_prior_loss, cw_prior_loss_args = prior_cw_loss_getter(values, targets)
cw_nll_loss, cw_nll_loss_args = nll_cw_loss_getter(values, targets)
def cw_loss(delta: float, value_index: np.int64, *cw_loss_args: tuple[Any, ...]) -> float:
    return cw_prior_loss(delta, value_index, *cw_loss_args[0]) + cw_nll_loss(delta, value_index, *cw_loss_args[1])
cw_loss_args = cw_prior_loss_args, cw_nll_loss_args

def test_data():
    assert prior(values, targets) == 0.
    assert prior(values + delta * eye[0], targets) == 1.
    assert prior(values - delta * eye[0], targets) == 1.
    assert prior(values + delta * eye[1], targets) == 1.
    assert prior(values - delta * eye[1], targets) == 1.
    assert nll(values, targets) == 1.
    assert nll(values + delta * eye[0], targets) == 2.
    assert nll(values - delta * eye[0], targets) == 2.
    assert nll(values + delta * eye[1], targets) == 2.
    assert nll(values - delta * eye[1], targets) == 2.

def test_loss_increase():
    values, targets = np.zeros(2), np.array([[-1., 0.], [1., 0.]])
    uncertainty = UncertaintyByLossIncrease(loss_increase=2.0, error=1e-1, max=1e3)
    lefts, rights = uncertainty(values, (targets,), prior_cw_loss_getter, nll_cw_loss_getter)
    assert all(np.abs(lefts - 1) < 1e-1)
    assert all(np.abs(rights - 1) < 1e-1)
    
def test_nll_increase():
    values, targets = np.zeros(2), np.array([0., 0.])
    uncertainty = NLLIncrease(nll_increase=1.0, error=1e-1, max=1e3)
    lefts, rights = uncertainty(values, (targets,), prior_cw_loss_getter, nll_cw_loss_getter)
    assert all(np.abs(lefts - np.sqrt(2)) < 1e-1)
    assert all(np.abs(rights - np.sqrt(2)) < 1e-1)
