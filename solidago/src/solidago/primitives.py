from typing import Union, Optional

import numpy as np
import numpy.typing as npt
from numba import njit

from solidago.solvers.optimize import njit_brentq as brentq


@njit
def qr_quantile(
    lipschitz: float,
    quantile: float,
    values: npt.NDArray,
    voting_rights: Union[npt.NDArray, float]=1.0,
    left_uncertainties: Optional[npt.NDArray]=None,
    right_uncertainties: Optional[npt.NDArray]=None,
    default_value: float=0.0,
    error: float=1e-5,
) -> float:
    """ Computes the quadratically regularized quantile, an estimate of 
    the quantile of values,weighted by voting_rights, given left and right 
    uncertainties, and with lipschitz resilience. 
    
    See "Solidago: A Modular Pipeline for Collaborative Scoring".
    
    Parameters
    ----------
    lipschitz: float
        Resilience parameters. Larger values are more resilient, but less accurate. 
    quantile: float
        Between 0 and 1.
    values: npt.ArrayLike
        Values whose quantile is estimated
    voting_rights: array or float
        Larger voting rights can pull the output towards them with more strength
    left_uncertainties: array or None
        Left uncertainty on each value. Set to zero if None.
    right_uncertainties: array or None
        Right uncertainty. Set to left_uncertainties if None (symmetric uncertainty).
    default_value: float
        Default value in the absence of data
    error: float
        Approximation error
    
    Returns
    --------
    out: float
        Lipschitz-resilient estimator of the quantile
    """
    assert quantile > 0 and quantile < 1
    
    if len(values) == 0:
        return default_value

    if left_uncertainties is None:
        left_uncertainties_2 = np.zeros(len(values))
    else:
        left_uncertainties_2 = left_uncertainties ** 2

    if right_uncertainties is None:
        right_uncertainties_2 = left_uncertainties_2
    else:
        right_uncertainties_2 = right_uncertainties ** 2

    # Brent’s method is used as a faster alternative to usual bisection
    return brentq(_qr_quantile_loss_derivative, xtol=error, args=(
        lipschitz, quantile, values, voting_rights, 
        left_uncertainties_2, right_uncertainties_2, default_value
    ))


@njit
def _qr_quantile_loss_derivative(
    variable: float,
    lipschitz: float,
    quantile: float,
    values: npt.NDArray,
    voting_rights: Union[npt.NDArray, float],
    left_uncertainties_2: npt.NDArray,
    right_uncertainties_2: npt.NDArray,
    default_value: float = 0.0,
    spacing: float = 1e-18,
):
    """Computes the derivative of the loss associated to qr_quantile"""
    regularization = (variable - default_value) / lipschitz

    deltas = variable - values
    uncertainties_2 = left_uncertainties_2 * (deltas < 0) + right_uncertainties_2 * (deltas > 0) + spacing
    forces = voting_rights * deltas / np.sqrt(uncertainties_2 + deltas**2)
    
    if quantile == 0.5:
        return regularization + forces.sum()
    
    left_strength = min(1.0, quantile / (1-quantile))
    right_strength = min(1.0, (1-quantile) / quantile)
    
    forces = np.where(
        forces < 0,
        forces * left_strength,
        forces * right_strength,
    )

    return regularization + forces.sum()


@njit
def qr_median(
    lipschitz: float,
    values: npt.NDArray,
    voting_rights: Union[npt.NDArray, float] = 1.0,
    left_uncertainties: Optional[npt.NDArray] = None,
    right_uncertainties: Optional[npt.NDArray] = None,
    default_value: float = 0.0,
    error: float = 1e-5,
):
    """ The quadratically regularized median is a Lipschitz-resilient median estimator. 
    It equals to the qr_quantile, for quantile = 0.5.
    
    See "Robust Sparse Voting", by Youssef Allouah, Rachid Guerraoui, Lê Nguyên Hoang
    and Oscar Villemaud, published at AISTATS 2024.
    
    Parameters
    ----------
    lipschitz: float
        Resilience parameters. Larger values are more resilient, but less accurate. 
    values: npt.ArrayLike
        Values whose quantile is estimated
    voting_rights: array or float
        Larger voting rights can pull the output towards them with more strength
    left_uncertainties: array or None
        Left uncertainty on each value. Set to zero if None.
    right_uncertainties: array or None
        Right uncertainty. Set to left_uncertainties if None (symmetric uncertainty).
    default_value: float
        Default value in the absence of data
    error: float
        Approximation error
    
    Returns
    --------
    out: float
        Lipschitz-resilient estimator of the median
    """
    return qr_quantile(lipschitz, 0.5, values, voting_rights, 
        left_uncertainties, right_uncertainties, default_value, error)


@njit
def qr_standard_deviation(
    lipschitz: float,
    values: npt.NDArray,
    quantile_dev: float = 0.5,
    voting_rights: Union[npt.NDArray, float] = 1.0,
    left_uncertainties: Optional[npt.NDArray] = None,
    right_uncertainties: Optional[npt.NDArray] = None,
    default_dev: float = 1.0,
    error: float = 1e-5,
    median: Optional[float] = None,
):
    """ Lipschitz-resilient estimator of the standard deviation.
    Can be understood as a measure of polarization.
    It roughly measures a median deviation from the median.
    
    For heavy-tail distributions of values, we however recommend
    selecting a higher quantile of deviations from the median.
    
    Parameters
    ----------
    lipschitz: float
        Resilience parameters. Larger values are more resilient, but less accurate. 
    values: npt.ArrayLike
        Values whose quantile is estimated
    quantile_dev: float
        Must be between 0 and 1. Defines the quantile of deviations from qr_med that is reported.
    voting_rights: array or float
        Larger voting rights can pull the output towards them with more strength
    left_uncertainties: array or None
        Left uncertainty on each value. Set to zero if None.
    right_uncertainties: array or None
        Right uncertainty. Set to left_uncertainties if None (symmetric uncertainty).
    default_dev: float
        Default value in the absence of data
    error: float
        Approximation error
    
    Returns
    --------
    out: float
        Lipschitz-resilient estimator of the quantile
    """
    assert quantile_dev > 0 and quantile_dev < 1

    if left_uncertainties is None:
        left_uncertainties = np.zeros(len(values))
    if right_uncertainties is None:
        right_uncertainties = left_uncertainties

    if median is None:
        median = qr_median(lipschitz, values, voting_rights, 
            left_uncertainties, right_uncertainties, error)

    deltas = values - median
    deviations = np.abs(deltas)
    left_uncertainties = left_uncertainties * (deltas > 0) + right_uncertainties * (deltas < 0)
    left_uncertainties = np.minimum(left_uncertainties, deviations)
    right_uncertainties = left_uncertainties * (deltas < 0) + right_uncertainties * (deltas > 0)

    return max(
        qr_quantile(
            lipschitz,
            quantile_dev,
            deviations,
            voting_rights,
            left_uncertainties,
            right_uncertainties,
            default_dev,
            error,
        ),
        0.0,
    )


@njit
def qr_uncertainty(
    lipschitz: float,
    values: npt.NDArray,
    voting_rights: Union[npt.NDArray, float] = 1.0,
    left_uncertainties: Optional[npt.NDArray] = None,
    right_uncertainties: Optional[npt.NDArray] = None,
    default_dev: float = 1.0,
    error: float = 1e-5,
    median: Optional[float] = None,
):
    """
    Quadratically regularized uncertainty
    TODO : search for a better formula for qr_uncertainty if possible
    """    
    return qr_standard_deviation(lipschitz, values, 0.5, voting_rights, left_uncertainties,
        right_uncertainties, default_dev, error, median)


@njit
def clip(values: np.ndarray, center: float, radius: float):
    return values.clip(center - radius, center + radius)


@njit
def clip_mean(
    voting_rights: np.ndarray, 
    values: np.ndarray, 
    center: float=0., 
    radius: float=1.,
):
    if len(values) == 0:
        return center
    return np.sum(voting_rights * clip(values, center, radius)) / np.sum(voting_rights)


@njit
def lipschitz_resilient_mean(
    lipschitz: float,
    values: npt.NDArray,
    voting_rights: Union[npt.NDArray[np.float64], float] = 1.0,
    left_uncertainties: Optional[npt.NDArray] = None,
    right_uncertainties: Optional[npt.NDArray] = None,
    default_value: float = 0.0,
    error: float = 1e-5,
):
    """ Lipschitz-robustified mean. Lipschitz-resilient mean estimator.
    It provably returns the mean, given sufficient participation and bounded values
    
    See "Robust Sparse Voting", by Youssef Allouah, Rachid Guerraoui, Lê Nguyên Hoang
    and Oscar Villemaud, published at AISTATS 2024.
    
    Parameters
    ----------
    lipschitz: float
        Resilience parameters. Larger values are more resilient, but less accurate. 
    values: npt.ArrayLike
        Values whose quantile is estimated
    voting_rights: array or float
        Larger voting rights can pull the output towards them with more strength
    left_uncertainties: array or None
        Left uncertainty on each value. Set to zero if None.
    right_uncertainties: array or None
        Right uncertainty. Set to left_uncertainties if None (symmetric uncertainty).
    default_value: float
        Default value in the absence of data
    error: float
        Approximation error
    
    Returns
    --------
    out: float
        Lipschitz-resilient estimator of the mean
    """
    if len(values) == 0:
        return default_value

    if isinstance(voting_rights, (float, int)):
        voting_rights = np.full(values.shape, voting_rights)

    total_voting_rights = np.sum(voting_rights)
    if total_voting_rights == 0.0:
        return default_value

    return clip_mean(
        voting_rights, 
        values, 
        center=qr_median(
            lipschitz=lipschitz/4, 
            values=values, 
            voting_rights=voting_rights, 
            left_uncertainties=left_uncertainties,
            right_uncertainties=right_uncertainties,
            default_value=default_value,
            error=error
        ), 
        radius=total_voting_rights * lipschitz / 4
    )
