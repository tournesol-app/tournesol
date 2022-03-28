from typing import Union

import numpy as np
import pandas as pd
from scipy.optimize import brentq

EPSILON = 1e-6


def QrMed(W: float, w: Union[pd.Series, float], x: pd.Series, delta: pd.Series):
    if isinstance(w, pd.Series):
        w = w.to_numpy()
    if isinstance(x, pd.Series):
        x = x.to_numpy()
    if isinstance(delta, pd.Series):
        delta = delta.to_numpy()
    delta_2 = delta ** 2

    def L_prime(m: float):
        x_minus_m = x - m
        return W * m - np.sum(w * x_minus_m / np.sqrt(delta_2 + x_minus_m ** 2))

    m_low = -1.0
    while L_prime(m_low) > 0:
        m_low *= 2

    m_up = 1.0
    while L_prime(m_up) < 0:
        m_up *= 2

    return brentq(L_prime, m_low, m_up, xtol=EPSILON)


def QrDev(
    W: float,
    default_dev: float,
    w: Union[pd.Series, float],
    x: pd.Series,
    delta: pd.Series,
    qr_med=None,
):
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
    h = W + np.sum(
        w * np.minimum(1, delta_2 * (delta_2 + (x - qr_med) ** 2) ** (-3 / 2))
    )

    if h <= W:
        return qr_dev

    k = (h - W) ** (-1 / 2)
    return (np.exp(-qr_dev) * qr_dev + np.exp(-k) * k) / (np.exp(-qr_dev) + np.exp(-k))


def Clip(x: np.ndarray, center, radius):
    return x.clip(center - radius, center + radius)


def ClipMean(w, x: np.ndarray, center, radius):
    return np.sum(w * Clip(x, center, radius)) / np.sum(w)


def BrMean(W, w, x, delta):
    if len(x) == 0:
        return 0.0
    if isinstance(w, float):
        w = np.full(x.shape, w)
    return ClipMean(w, x, center=QrMed(4 * W, w, x, delta), radius=np.sum(w) / (4 * W))
