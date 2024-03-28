import logging

import pandas as pd

from solidago.pipeline import TournesolInput
from solidago.primitives import qr_quantile, qr_standard_deviation
from .scaling_step import compute_scaling


def compute_individual_scalings(
    individual_scores: pd.DataFrame,
    tournesol_input: TournesolInput,
    W: float,
) -> pd.DataFrame:
    """
    Inputs:
    - individual_scores: DataFrame with columns
        * user_id
        * entity_id
        * raw_score
        * raw_uncertainty

    - tournesol_input: TournesolInput used to fetch user details (used in calibration step)

    Returns:
    - scalings: DataFrame with index `user_id` and columns:
        * `s`: scaling factor
        * `tau`: translation value
        * `delta_s`: uncertainty on `s`
        * `delta_tau`: uncertainty on `tau`
    """
    if len(individual_scores) == 0:
        return pd.DataFrame(
            columns=["s", "tau", "delta_s", "delta_tau"]
        )

    ratings = tournesol_input.ratings_properties.set_index(["user_id", "entity_id"])

    # Calibration
    calibration_ratings =  ratings[ratings.is_scaling_calibration_user]
    calibration_users_scores = individual_scores.join(calibration_ratings, on=["user_id", "entity_id"], how="inner")
    ## Init columns "score" and "uncertainty" read by `compute_scaling()`
    calibration_users_scores["score"] = calibration_users_scores["raw_score"]
    calibration_users_scores["uncertainty"] = calibration_users_scores["raw_uncertainty"]
    calibration_users_scalings = compute_scaling(
        calibration_users_scores,
        tournesol_input=tournesol_input,
        W=W,
        calibration=True,
    )

    non_calibration_user_ids = ratings[~ratings.is_scaling_calibration_user].index.unique("user_id")
    calibration_user_ids = ratings[ratings.is_scaling_calibration_user].index.unique("user_id")
    all_users_scores = individual_scores.join(ratings, on=["user_id", "entity_id"], how="left")
    all_users_scores["is_public"].fillna(False, inplace=True)
    all_users_scores["is_scaling_calibration_user"].fillna(False, inplace=True)

    # Apply scaling for calibration users
    all_users_scores = apply_scalings(all_users_scores, scalings=calibration_users_scalings)

    # Apply scaling for non-calibration users
    logging.info(
        "Computing scaling for %s non-calibration users, based on %s calibration users",
        len(non_calibration_user_ids),
        len(calibration_user_ids),
    )
    non_calibration_users_scalings = compute_scaling(
        all_users_scores,
        tournesol_input=tournesol_input,
        users_to_compute=non_calibration_user_ids,
        reference_users=calibration_user_ids,
        calibration=False,
        W=W,
    )
    all_users_scalings = pd.concat(
        df
        for df in [calibration_users_scalings, non_calibration_users_scalings]
        if not df.empty
    )
    return all_users_scalings


def apply_scalings(individual_scores: pd.DataFrame, scalings: pd.DataFrame) -> pd.DataFrame:
    df = individual_scores.join(scalings, on="user_id")
    df["s"].fillna(1.0, inplace=True)
    df["tau"].fillna(0.0, inplace=True)
    df["delta_s"].fillna(0.0, inplace=True)
    df["delta_tau"].fillna(0.0, inplace=True)
    df["score"] = df["s"] * df["raw_score"] + df["tau"]
    df["uncertainty"] = (
        df["s"] * df["raw_uncertainty"] + df["delta_s"] * df["raw_score"].abs() + df["delta_tau"]
    )
    return df.drop(columns=["s", "tau", "delta_s", "delta_tau"])


def estimate_positive_score_shift(
    scaled_individual_scores: pd.DataFrame, W: float, quantile: float = 0.05
) -> float:
    w = 1 / scaled_individual_scores.groupby("user_id")["score"].transform("size")
    x = scaled_individual_scores.score
    delta = scaled_individual_scores.uncertainty
    return qr_quantile(
        lipschitz=1/W,
        quantile=quantile,
        values=x.to_numpy(),
        voting_rights=w.to_numpy(),
        left_uncertainties=delta.to_numpy(),
    )


def estimate_score_deviation(scaled_individual_scores, W, quantile=0.5):
    w = 1 / scaled_individual_scores.groupby("user_id")["score"].transform("size")
    x = scaled_individual_scores.score
    delta = scaled_individual_scores.uncertainty
    return qr_standard_deviation(
        lipschitz=1/W,
        values=x.to_numpy(),
        quantile_dev=quantile,
        voting_rights=w.to_numpy(),
        left_uncertainties=delta.to_numpy(),
    )
