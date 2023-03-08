from typing import Union

import numpy as np
import pandas as pd
from scipy.optimize import brentq

EPSILON = 1e-6  # convergence tolerance


def QrMed(W: float, w: Union[pd.Series, float], x: pd.Series, delta: pd.Series):
    """
    Quadratically regularized median.
    It behaves like a weighted median biased towards 0.

    Parameters:
        * `W`: Byzantine resilience parameter.
            The influence of a single contributor 'i' is bounded by (w_i/W)
        * `w`: voting rights vector
        * `x`: partial scores vector
        * `delta`: partial scores uncertainties vector
    """
    if len(x) == 0:
        return 0.0
    if isinstance(w, pd.Series):
        w = w.to_numpy()
    if isinstance(x, pd.Series):
        x = x.to_numpy()
    if isinstance(delta, pd.Series):
        delta = delta.to_numpy()
    # Set a minimum value to prevent divisions by zero in L_prime
    delta_2 = np.where(delta > 0, delta ** 2, np.spacing(0))

    def L_prime(m: float):
        x_minus_m = x - m
        return W * m - np.sum(w * x_minus_m / np.sqrt(delta_2 + x_minus_m ** 2))

    m_low = -1.0
    while L_prime(m_low) > 0:
        m_low *= 2

    m_up = 1.0
    while L_prime(m_up) < 0:
        m_up *= 2

    # Brent’s method is used as a faster alternative to usual bisection
    return brentq(L_prime, m_low, m_up, xtol=EPSILON)


def QrDev(
    W: float,
    default_dev: float,
    w: Union[pd.Series, float],
    x: pd.Series,
    delta: pd.Series,
    qr_med=None,
):
    """
    Quadratically regularized deviation, between x and their QrMed.
    Can be understood as a measure of polarization.
    It is like a secure version of the median deviation from the median.
    """
    if qr_med is None:
        qr_med = QrMed(W, w, x, delta)
    return default_dev + QrMed(W, w, np.abs(x - qr_med) - default_dev, delta)


def QrUnc(
    W: float,
    default_dev: float,
    w: pd.Series,
    x: pd.Series,
    delta: pd.Series,
    qr_med=None,
):
    """
    Quadratically regularized uncertainty
    TODO : search for a better formula for QrUnc if possible
    """
    if isinstance(w, pd.Series):
        w = w.to_numpy()
    if isinstance(x, pd.Series):
        x = x.to_numpy()
    if isinstance(delta, pd.Series):
        delta = delta.to_numpy()

    if qr_med is None:
        qr_med = QrMed(W, w, x, delta)
    qr_dev = QrDev(W, default_dev, w, x, delta, qr_med=qr_med)
    delta_2 = delta ** 2
    bound = np.inf if W <= 0 else 1 / W
    h = W + np.sum(
        w * np.minimum(bound, delta_2 * (delta_2 + (x - qr_med) ** 2) ** (-3 / 2))
    )

    if h <= W:
        return qr_dev

    k = (h - W) ** (-1 / 2)

    # Use LogSumExp with a negative value of alpha to have a smooth minimum instead
    # of a smooth maximum (c.f. https://github.com/tournesol-app/tournesol/issues/1232).
    alpha = -1.0
    return np.maximum(0.0, alpha * np.log(np.exp(alpha * qr_dev) + np.exp(alpha * k)))


def Clip(x: np.ndarray, center: float, radius: float):
    return x.clip(center - radius, center + radius)


def ClipMean(w: np.ndarray, x: np.ndarray, center: float, radius: float):
    return np.sum(w * Clip(x, center, radius)) / np.sum(w)


def BrMean(W: float, w: Union[float, np.ndarray], x: np.ndarray, delta: np.ndarray):
    """
    Byzantine-robustified mean
    """
    if len(x) == 0:
        return 0.0
    if isinstance(w, float):
        w = np.full(x.shape, w)
    return ClipMean(w, x, center=QrMed(4 * W, w, x, delta), radius=np.sum(w) / (4 * W))
