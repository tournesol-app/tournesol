from typing import Tuple

import pandas as pd
import numpy as np

from solidago.resilient_primitives import QrQuantile, QrDev



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


def estimate_positive_score_shift(scaled_individual_scores: pd.DataFrame, W: float,quantile: float = 0.05) -> float:
    user_counts = scaled_individual_scores.user_id.value_counts("user_id")
    w = scaled_individual_scores.user_id.apply(lambda u: 1 / user_counts[u])
    x = scaled_individual_scores.score
    delta = scaled_individual_scores.uncertainty
    return QrQuantile(W, w, x, delta, quantile)

def estimate_score_std(scaled_individual_scores, W):
    # TODO This computes much smaller deviations than expected. We should figure it out
    user_counts = scaled_individual_scores.user_id.value_counts("user_id")
    w = scaled_individual_scores.user_id.apply(lambda u: 1) #/ user_counts[u])
    x = scaled_individual_scores.score
    delta = scaled_individual_scores.uncertainty
    default_deviation = 1
    return QrDev(W, default_deviation, w, x, delta)
    