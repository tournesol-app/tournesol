import numpy as np
import pandas as pd

from solidago.resilient_primitives import QrQuantile, QrDev, QrMed


def compute_individual_scalings(individual_scores: pd.DataFrame) -> pd.DataFrame:
    """
    Inputs:
    - individual_scores: DataFrame with columns
        * user_id
        * entity_id
        * score
        * score_uncertainty

    Returns:
    - scalings: DataFrame with index `user_id` and columns:
        * `s`: scaling factor
        * `tau`: translation value
        * `delta_s`: uncertainty on `s`
        * `delta_tau`: uncertainty on `tau`
    """
    raise NotImplementedError("To be coming soon")


def apply_scalings(individual_scores: pd.DataFrame, scalings: pd.DataFrame) -> pd.DataFrame:
    raise NotImplementedError("To be coming soon")


def estimate_positive_score_shift(
    scaled_individual_scores: pd.DataFrame, W: float, quantile: float = 0.05
) -> float:
    w = 1 / scaled_individual_scores.groupby("user_id")["score"].transform("size")
    x = scaled_individual_scores.score
    delta = scaled_individual_scores.uncertainty
    return QrQuantile(W, w, x, delta, quantile)


def estimate_score_deviation(scaled_individual_scores, W, quantile=0.5):
    w = 1 / scaled_individual_scores.groupby("user_id")["score"].transform("size")
    x = scaled_individual_scores.score
    delta = scaled_individual_scores.uncertainty
    qr_med = QrMed(W=W, w=w, x=x, delta=delta)
    return QrQuantile(W=W, w=w, x=np.abs(x-qr_med), delta=delta, quantile=quantile)
