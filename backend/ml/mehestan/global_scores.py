import logging
from typing import Tuple

import numpy as np
import pandas as pd

from ml.inputs import MlInput

from .primitives import BrMean, QrDev, QrMed, QrUnc

# `W` is the Byzantine resilience parameter,
# i.e the number of voting rights needed to modify a global score by 1 unit.
W = 20.0
SCALING_WEIGHT_CALIBRATION = W


def get_user_scaling_weights(ml_input: MlInput):
    ratings_properties = ml_input.ratings_properties[
        ["user_id", "trust_score", "is_scaling_calibration_user"]
    ].copy()
    df = ratings_properties.groupby("user_id").first()
    df["scaling_weight"] = df["trust_score"]
    df["scaling_weight"].mask(
        df.is_scaling_calibration_user,
        SCALING_WEIGHT_CALIBRATION,
        inplace=True,
    )
    return df["scaling_weight"].to_dict()


def get_significantly_different_pairs(scores: pd.DataFrame):
    """
    Find the set of pairs of alternatives
    that are significantly different, according to the contributor scores.
    (Used for collaborative preference scaling)
    """
    scores = scores[["uid", "score", "uncertainty"]]
    left, right = np.triu_indices(len(scores), k=1)
    pairs = (
        scores.iloc[left]
        .reset_index(drop=True)
        .join(
            scores.iloc[right].reset_index(drop=True),
            lsuffix="_a",
            rsuffix="_b",
        )
    )
    pairs.set_index(["uid_a", "uid_b"], inplace=True)
    return pairs.loc[
        np.abs(pairs.score_a - pairs.score_b)
        >= 2 * (pairs.uncertainty_a + pairs.uncertainty_b)
    ]


def compute_scaling(
    df: pd.DataFrame,
    ml_input: MlInput,
    users_to_compute=None,
    reference_users=None,
    calibration=False,
):
    scaling_weights = get_user_scaling_weights(ml_input)
    df = df.rename({"entity_id": "uid"}, axis=1)

    if users_to_compute is None:
        users_to_compute = set(df.user_id.unique())
    else:
        users_to_compute = set(users_to_compute)

    if reference_users is None:
        reference_users = set(df.user_id.unique())
    else:
        reference_users = set(reference_users)

    s_dict = {}
    delta_s_dict = {}

    for (user_n, user_scores) in df[df.user_id.isin(users_to_compute)].groupby(
        "user_id"
    ):
        s_nqm = []
        delta_s_nqm = []
        s_weights = []

        ABn_all = get_significantly_different_pairs(user_scores)
        user_scores_uids = set(ABn_all.index.get_level_values("uid_a")) | set(
            ABn_all.index.get_level_values("uid_b")
        )

        for (user_m, m_scores) in df[
            df.user_id.isin(reference_users - {user_n})
        ].groupby("user_id"):
            common_uids = user_scores_uids.intersection(m_scores.uid)

            if len(common_uids) == 0:
                continue

            m_scores = m_scores[m_scores.uid.isin(common_uids)]
            ABm = get_significantly_different_pairs(m_scores)
            ABnm = ABn_all.join(ABm, how="inner", lsuffix="_n", rsuffix="_m")
            if len(ABnm) == 0:
                continue
            s_nqmab = np.abs(ABnm.score_a_m - ABnm.score_b_m) / np.abs(
                ABnm.score_a_n - ABnm.score_b_n
            )

            delta_s_nqmab = (
                (
                    np.abs(ABnm.score_a_m - ABnm.score_b_m)
                    + ABnm.uncertainty_a_m
                    + ABnm.uncertainty_b_m
                )
                / (
                    np.abs(ABnm.score_a_n - ABnm.score_b_n)
                    - ABnm.uncertainty_a_n
                    - ABnm.uncertainty_b_n
                )
            ) - s_nqmab

            s = QrMed(1, 1, s_nqmab - 1, delta_s_nqmab)
            s_nqm.append(s + 1)
            delta_s_nqm.append(QrUnc(1, 1, 1, s_nqmab - 1, delta_s_nqmab, qr_med=s))
            s_weights.append(scaling_weights[user_m])

        s_weights = np.array(s_weights)
        theta_inf = np.max(user_scores.score.abs())
        s_nqm = np.array(s_nqm)
        delta_s_nqm = np.array(delta_s_nqm)
        if calibration:
            s_dict[user_n] = 1 + BrMean(8 * W * theta_inf, s_weights, s_nqm - 1, delta_s_nqm)
            delta_s_dict[user_n] = QrUnc(8 * W * theta_inf, 1, s_weights, s_nqm - 1, delta_s_nqm)
        else:
            qr_med = QrMed(8 * W * theta_inf, s_weights, s_nqm - 1, delta_s_nqm)
            s_dict[user_n] = 1 + qr_med
            delta_s_dict[user_n] = QrUnc(
                8 * W * theta_inf, 1, s_weights, s_nqm - 1, delta_s_nqm, qr_med=qr_med
            )

    tau_dict = {}
    delta_tau_dict = {}
    for (user_n, user_scores) in df[df.user_id.isin(users_to_compute)].groupby(
        "user_id"
    ):
        tau_nqm = []
        delta_tau_nqm = []
        s_weights = []
        for (user_m, m_scores) in df[
            df.user_id.isin(reference_users - {user_n})
        ].groupby("user_id"):
            common_uids = list(set(user_scores.uid).intersection(m_scores.uid))

            if len(common_uids) == 0:
                continue

            m_scores = m_scores.set_index("uid").loc[common_uids]
            n_scores = user_scores.set_index("uid").loc[common_uids]

            tau_nqmab = (
                s_dict.get(user_m, 1) * m_scores.score - s_dict[user_n] * n_scores.score
            )
            delta_tau_nqmab = (
                s_dict[user_n] * n_scores.uncertainty
                + s_dict.get(user_m, 1) * m_scores.uncertainty
            )

            tau = QrMed(1, 1, tau_nqmab, delta_tau_nqmab)
            tau_nqm.append(tau)
            delta_tau_nqm.append(QrUnc(1, 1, 1, tau_nqmab, delta_tau_nqmab, qr_med=tau))
            s_weights.append(scaling_weights[user_m])

        s_weights = np.array(s_weights)
        tau_nqm = np.array(tau_nqm)
        delta_tau_nqm = np.array(delta_tau_nqm)
        if calibration:
            tau_dict[user_n] = BrMean(8 * W, s_weights, tau_nqm, delta_tau_nqm)
            delta_tau_dict[user_n] = QrUnc(8 * W, 1, s_weights, tau_nqm, delta_tau_nqm)
        else:
            qr_med = QrMed(8 * W, s_weights, tau_nqm, delta_tau_nqm)
            tau_dict[user_n] = qr_med
            delta_tau_dict[user_n] = QrUnc(
                8 * W, 1, s_weights, tau_nqm, delta_tau_nqm, qr_med=qr_med
            )

    return pd.DataFrame(
        {
            "s": s_dict,
            "tau": tau_dict,
            "delta_s": delta_s_dict,
            "delta_tau": delta_tau_dict,
        }
    )


def get_scaling_for_calibration(ml_input: MlInput, individual_scores: pd.DataFrame):
    rp = ml_input.ratings_properties
    rp = rp.set_index(["user_id", "entity_id"])
    rp = rp[rp.is_scaling_calibration_user]
    df = individual_scores.join(rp, on=["user_id", "entity_id"], how="inner")
    df["score"] = df["raw_score"]
    df["uncertainty"] = df["raw_uncertainty"]
    return compute_scaling(df, ml_input=ml_input, calibration=True)


def compute_scaled_scores(
    ml_input: MlInput, individual_scores: pd.DataFrame
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Returns:
        - scaled individual scores: Dataframe with columns
            * `user_id`
            * `entity_id`
            * `raw_score`
            * `raw_uncertainty`
            * `score`
            * `uncertainty`
            * `is_public`
            * `is_scaling_calibration_user`
        - scalings: DataFrame with index `entity_id` and columns:
            * `s`: scaling factor
            * `tau`: translation value
            * `delta_s`: uncertainty on `s`
            * `delta_tau`: uncertainty on `tau`
    """
    if len(individual_scores) == 0:
        scores = pd.DataFrame(
            columns=[
                "user_id",
                "entity_id",
                "raw_score",
                "raw_uncertainty",
                "score",
                "uncertainty",
                "is_public",
                "is_scaling_calibration_user",
                "trust_score",
            ]
        )
        scalings = pd.DataFrame(columns=["s", "tau", "delta_s", "delta_tau"])
        return scores, scalings
    calibration_scaling = get_scaling_for_calibration(ml_input, individual_scores)
    rp = ml_input.ratings_properties

    non_calibration_users = rp["user_id"][~rp.is_scaling_calibration_user].unique()
    calibration_users = rp["user_id"][rp.is_scaling_calibration_user].unique()
    rp = rp.set_index(["user_id", "entity_id"])
    df = individual_scores.join(rp, on=["user_id", "entity_id"], how="left")
    df["is_public"].fillna(False, inplace=True)
    df["is_scaling_calibration_user"].fillna(False, inplace=True)

    # Apply scaling for calibration users
    df = df.join(calibration_scaling, on="user_id")
    df["s"].fillna(1, inplace=True)
    df["tau"].fillna(0, inplace=True)
    df["delta_s"].fillna(0, inplace=True)
    df["delta_tau"].fillna(0, inplace=True)
    df["score"] = df["s"] * df["raw_score"] + df["tau"]
    df["uncertainty"] = (
        df["s"] * df["raw_uncertainty"]
        + df["delta_s"] * df["raw_score"].abs()
        + df["delta_tau"]
    )
    df.drop(["s", "tau", "delta_s", "delta_tau"], axis=1, inplace=True)

    # Apply scaling for non-calibration users
    logging.info(
        "Computing scaling for %s non-calibration users, based on %s calibration users",
        len(non_calibration_users),
        len(calibration_users),
    )
    non_calibration_scaling = compute_scaling(
        df,
        ml_input=ml_input,
        users_to_compute=non_calibration_users,
        reference_users=calibration_users,
        calibration=False,
    )

    df = df.join(non_calibration_scaling, on="user_id")
    df["is_scaling_calibration_user"].fillna(False, inplace=True)

    df["s"].fillna(1, inplace=True)
    df["tau"].fillna(0, inplace=True)
    df["delta_s"].fillna(0, inplace=True)
    df["delta_tau"].fillna(0, inplace=True)
    df.loc[~df["is_scaling_calibration_user"], "uncertainty"] = (
        df["s"] * df["raw_uncertainty"]
        + df["delta_s"] * df["raw_score"].abs()
        + df["delta_tau"]
    )
    df.loc[~df["is_scaling_calibration_user"], "score"] = df["raw_score"] * df["s"] + df["tau"]
    df.drop(
        ["s", "tau", "delta_s", "delta_tau"],
        axis=1,
        inplace=True,
    )
    all_scalings = pd.concat([calibration_scaling, non_calibration_scaling])
    return df, all_scalings


def get_global_scores(scaled_scores: pd.DataFrame):
    if len(scaled_scores) == 0:
        return pd.DataFrame(
            columns=["entity_id", "score", "uncertainty", "deviation", "n_contributors"]
        )

    global_scores = {}
    for (entity_id, scores) in scaled_scores.groupby("entity_id"):
        w = scores.voting_right
        theta = scores.score
        delta = scores.uncertainty
        rho = QrMed(2 * W, w, theta, delta)
        rho_uncertainty = QrUnc(2 * W, 1, w, theta, delta, qr_med=rho)
        rho_deviation = QrDev(2 * W, 1, w, theta, delta, qr_med=rho)
        global_scores[entity_id] = {
            "score": rho,
            "uncertainty": rho_uncertainty,
            "deviation": rho_deviation,
            "n_contributors": len(scores),
        }

    result = pd.DataFrame.from_dict(global_scores, orient="index")
    result.index.name = "entity_id"
    return result.reset_index()
