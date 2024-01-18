from typing import Union

import numpy as np
import numpy.typing as npt
import pandas as pd
from numba import njit

from solidago.solvers.optimize import brentq


def qr_quantile(
    lipschitz: float, 
    quantile: float,
    values: npt.ArrayLike, 
    voting_rights: Union[npt.ArrayLike, float] = 1, 
    left_uncertainties: Optional[npt.ArrayLike] = None,    
    right_uncertainties: Optional[npt.ArrayLike] = None,
    default_value: float = 0,
    error: float = 1e-5
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
        left_uncertainties = np.zeros(len(values))
    if right_uncertainties is None:
        right_uncertainties = left_uncertainties

    # Brent’s method is used as a faster alternative to usual bisection
    return brentq(_qr_quantile_loss_derivative, xtol=error, args=(
        quantile, lipschitz, voting_rights, values, 
        left_uncertainties, right_uncertainties, default_value
    ))

@njit
def _qr_quantile_loss_derivative(
    variable: float, 
    quantile: float,
    lipschitz: float, 
    voting_rights: Union[npt.NDArray, float],
    values: npt.NDArray, 
    left_uncertainties: npt.NDArray, 
    right_uncertainties: npt.NDArray, 
    default_value: float = 0
):
    """ Computes the derivative of the loss associated to QrQuantile """
    regularization = (variable - default_value) / lipschitz
    quantile_term = 0 if quantile == 0.5 else (1 - 2 * quantile) * np.sum(voting_rights)
    
    deltas = variable - values
    uncertainties = left_uncertainties * (deltas < 0) + right_uncertainties * (deltas > 0)
    forces = np.sum( voting_rights * deltas / np.sqrt(uncertainties**2 + deltas**2) )
    
    return regularization + quantile_term + forces

   
def qr_median(
    lipschitz: float, 
    values: npt.ArrayLike, 
    voting_rights: Union[npt.ArrayLike, float] = 1, 
    left_uncertainties: Optional[npt.ArrayLike] = None,    
    right_uncertainties: Optional[npt.ArrayLike] = None,
    error: float = 1e-5
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
    return qr_quantile(lipschitz, 0.5, voting_rights, values, 
        left_uncertainties, right_uncertainties, error)


def qr_standard_deviation(
    lipschitz: float, 
    values: npt.ArrayLike, 
    quantile_dev: float = 0.5,
    voting_rights: Union[npt.ArrayLike, float] = 1, 
    left_uncertainties: Optional[npt.ArrayLike] = None,    
    right_uncertainties: Optional[npt.ArrayLike] = None,
    default_dev: float = 0,
    error: float = 1e-5,
    median: float = None,
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
    
    if median is None:
        median = QrMedian(lipschitz, values, voting_rights, 
            left_uncertainties, right_uncertainties, error)
    
    deltas = values - median
    deviations = np.abs(deltas)
    left_uncertainties = left_uncertainties * (deltas > 0) + right_uncertainties * (deltas < 0)
    left_uncertainties = np.minimum(left_uncertainties, deviations)
    right_uncertainties = left_uncertainties * (deltas < 0) + right_uncertainties * (deltas > 0)
       
    return max(qr_quantile(lipschitz, quantile_dev,deviations, voting_rights, 
        left_uncertainties, right_uncertainties, default_dev, error), 0)

def qr_uncertainty(
    lipschitz: float, 
    values: npt.ArrayLike, 
    voting_rights: Union[npt.ArrayLike, float] = 1, 
    left_uncertainties: Optional[npt.ArrayLike] = None,    
    right_uncertainties: Optional[npt.ArrayLike] = None,
    default_uncertainty: float = 1,
    error: float = 1e-5,
    median: float = None,
):
    """
    Quadratically regularized uncertainty
    TODO : search for a better formula for QrUnc if possible
    """    
    if median is None:
        median = QrMedian(lipschitz, values, voting_rights, 
            left_uncertainties, right_uncertainties, error)
    
    square_uncertainties = (left_uncertainties + right_uncertainties)**2 / 4
    
    delta_2 = delta**2
    nonregularized_capped_second_derivative = np.sum(
        voting_rights * np.minimum(
            lipschitz, 
            square_uncertainties * (square_uncertainties + (values - median) ** 2) ** (-3 / 2)
        )
    )
    return (
        (default_dev**-2) 
        + 2 * default_dev**-3 * nonregularized_capped_second_derivative
    ) ** (-1 / 2)


def clip(values: np.ndarray, center: float, radius: float):
    return values.clip(center - radius, center + radius)


def clip_mean(voting_rights: np.ndarray, values: np.ndarray, center: float, radius: float):
    return np.sum(voting_rights * clip(values, center, radius)) / np.sum(voting_rights)


def br_mean(
    lipschitz: float, 
    voting_rights: Union[float, np.ndarray], 
    values: np.ndarray, 
    uncertainties: np.ndarray,
    default_value: float,
    error: float=1e-5
):
    """ Byzantine-robustified mean. Lipschitz-resilient mean estimator.
    It provably returns the mean, given sufficient participation and bounded values
    """
    if len(values) == 0:
        return default_value
        
    if isinstance(voting_rights, float):
        voting_rights = np.full(values.shape, voting_rights)
        
    return clip_mean(
        voting_rights, 
        values, 
        qr_median(lipschitz/4, voting_rights, values, uncertainties, error=error), 
        np.sum(voting_rights) * lipschitz / 4
    )



