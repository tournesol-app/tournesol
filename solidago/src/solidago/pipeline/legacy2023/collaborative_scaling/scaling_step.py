import numpy as np
import pandas as pd
from numba import njit

from solidago.pipeline import TournesolInput
from solidago.primitives import (
    lipschitz_resilient_mean,
    qr_median,
    qr_uncertainty,
)


# This limit allows to index pairs of entity_id into a usual Index with dtype 'uint64'.
# We originally used a MultiIndex that consumed significantly more memory, due to how
# pandas may cache MultiIndex values as an array of Python tuples.
ENTITY_ID_MAX = 2**32 - 1


@njit
def get_significantly_different_pairs_indices(scores, uncertainties):
    indices = []
    n_alternatives = len(scores)
    for idx_a in range(0, n_alternatives):
        for idx_b in range(idx_a + 1, n_alternatives):
            if abs(scores[idx_a] - scores[idx_b]) >= 2 * (
                uncertainties[idx_a] + uncertainties[idx_b]
            ):
                indices.append((idx_a, idx_b))
    if len(indices) == 0:
        return np.empty((0, 2), dtype=np.int64)
    return np.array(indices)



def get_user_scaling_weights(input: TournesolInput, W: float):
    ratings_properties = input.ratings_properties[
        ["user_id", "trust_score", "is_scaling_calibration_user"]
    ].copy()
    df = ratings_properties.groupby("user_id").first()
    df["scaling_weight"] = df["trust_score"]
    df["scaling_weight"].mask(
        df.is_scaling_calibration_user,
        W,
        inplace=True,
    )
    return df["scaling_weight"].to_dict()


def get_significantly_different_pairs(scores: pd.DataFrame):
    """
    Find the set of pairs of alternatives
    that are significantly different, according to the contributor scores.
    (Used for collaborative preference scaling)
    """
    scores = scores[["entity_id", "score", "uncertainty"]]
    indices = get_significantly_different_pairs_indices(
        scores["score"].to_numpy(), scores["uncertainty"].to_numpy()
    )
    scores_a = scores.iloc[indices[:, 0]]
    scores_b = scores.iloc[indices[:, 1]]

    entity_pairs_index = pd.Index(
        # As a memory optimization, a pair of entity_id is represented as a single uint64
        scores_a["entity_id"].to_numpy() * (ENTITY_ID_MAX + 1) + scores_b["entity_id"].to_numpy(),
        dtype="uint64",
    )
    return pd.DataFrame(
        {
            "score_a": scores_a["score"].to_numpy(),
            "score_b": scores_b["score"].to_numpy(),
            "uncertainty_a": scores_a["uncertainty"].to_numpy(),
            "uncertainty_b": scores_b["uncertainty"].to_numpy(),
        },
        index=entity_pairs_index,
    )


def compute_scaling(
    df: pd.DataFrame,
    tournesol_input: TournesolInput,
    W: float,
    users_to_compute=None,
    reference_users=None,
    calibration=False,
):
    scaling_weights = get_user_scaling_weights(tournesol_input, W=W)

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

    if len(df) > 0 and df["entity_id"].max() > ENTITY_ID_MAX:
        raise AssertionError("Values of entity_id are too large.")

    ref_user_scores_pairs = {}
    ref_user_scores_by_entity_id = {}
    for (ref_user_id, ref_user_scores) in df[df["user_id"].isin(reference_users)].groupby(
        "user_id"
    ):
        ref_user_scores_pairs[ref_user_id] = get_significantly_different_pairs(ref_user_scores)
        ref_user_scores_by_entity_id[ref_user_id] = ref_user_scores.set_index("entity_id")

    for (user_n, user_n_scores) in df[df["user_id"].isin(users_to_compute)].groupby("user_id"):
        s_nqm = []
        delta_s_nqm = []
        s_weights = []

        if calibration:
            ABn_all = ref_user_scores_pairs[user_n]
        else:
            ABn_all = get_significantly_different_pairs(user_n_scores)

        if len(ABn_all) > 0:
            ABn_all_index_set = set(ABn_all.index)
            for user_m in reference_users - {user_n}:
                try:
                    ABm = ref_user_scores_pairs[user_m]
                except KeyError:
                    # the reference user may not have contributed on the current criterion
                    continue

                if all((idx not in ABn_all_index_set) for idx in ABm.index):
                    # Quick path: the intersection is empty, no need to call expensive inner join.
                    continue

                ABnm = ABn_all.join(ABm, how="inner", lsuffix="_n", rsuffix="_m")
                s_nqmab = (
                    (ABnm.score_a_m - ABnm.score_b_m).abs()
                    / (ABnm.score_a_n - ABnm.score_b_n).abs()
                ).to_numpy()
                delta_s_nqmab = ((
                    (
                        (ABnm.score_a_m - ABnm.score_b_m).abs()
                        + ABnm.uncertainty_a_m
                        + ABnm.uncertainty_b_m
                    )
                    / (
                        (ABnm.score_a_n - ABnm.score_b_n).abs()
                        - ABnm.uncertainty_a_n
                        - ABnm.uncertainty_b_n
                    )
                ) - s_nqmab).to_numpy()

                s = qr_median(
                    lipschitz=1.0,
                    voting_rights=1.0,
                    values=s_nqmab - 1,
                    left_uncertainties=delta_s_nqmab,
                )
                s_nqm.append(s + 1)
                delta_s_nqm.append(qr_uncertainty(
                    lipschitz=1.0,
                    default_dev=1.0,
                    voting_rights=1.0,
                    values=s_nqmab - 1,
                    left_uncertainties=delta_s_nqmab,
                    median=s,
                ))
                s_weights.append(scaling_weights[user_m])

        s_weights = np.array(s_weights)
        theta_inf = np.max(user_n_scores.score.abs())
        s_nqm = np.array(s_nqm)
        delta_s_nqm = np.array(delta_s_nqm)
        lipshitz = 1/(8*W*theta_inf) if theta_inf > 0.0 else 1e18
        if calibration:
            s_dict[user_n] = lipschitz_resilient_mean(
                lipschitz=lipshitz,
                values=s_nqm,
                voting_rights=s_weights,
                left_uncertainties=delta_s_nqm,
                default_value=1.0,
            )
            delta_s_dict[user_n] = qr_uncertainty(
                lipschitz=lipshitz,
                default_dev=1.0,
                values=s_nqm,
                voting_rights=s_weights,
                left_uncertainties=delta_s_nqm,
            )
        else:
            qr_med = qr_median(
                lipschitz=lipshitz,
                voting_rights=s_weights,
                values=s_nqm - 1,
                left_uncertainties=delta_s_nqm,
            )
            s_dict[user_n] = 1 + qr_med
            delta_s_dict[user_n] = qr_uncertainty(
                lipschitz=lipshitz,
                default_dev=1.0,
                voting_rights=s_weights,
                values=s_nqm-1,
                left_uncertainties=delta_s_nqm,
                median=qr_med,
            )

    tau_dict = {}
    delta_tau_dict = {}
    for (user_n, user_n_scores) in df[df.user_id.isin(users_to_compute)].groupby("user_id"):
        tau_nqm = []
        delta_tau_nqm = []
        s_weights = []
        user_n_scores = user_n_scores.set_index("entity_id")
        user_n_scores_entity_ids = set(user_n_scores.index)

        for user_m in reference_users - {user_n}:
            try:
                user_m_scores = ref_user_scores_by_entity_id[user_m]
            except KeyError:
                # the reference user may not have contributed on the current criterion
                continue
            common_entity_ids = list(user_n_scores_entity_ids.intersection(user_m_scores.index))
            if len(common_entity_ids) == 0:
                continue

            m_scores = user_m_scores.loc[common_entity_ids]
            n_scores = user_n_scores.loc[common_entity_ids]

            s_m = s_dict.get(user_m, 1)
            s_n = s_dict[user_n]
            tau_nqmab = (s_m * m_scores.score - s_n * n_scores.score).to_numpy()
            delta_tau_nqmab = (s_n * n_scores.uncertainty + s_m * m_scores.uncertainty).to_numpy()

            tau = qr_median(
                lipschitz=1.0,
                voting_rights=1.0,
                values=tau_nqmab,
                left_uncertainties=delta_tau_nqmab,
            )
            tau_nqm.append(tau)
            delta_tau_nqm.append(qr_uncertainty(
                lipschitz=1.0,
                default_dev=1.0,
                voting_rights=1.0,
                values=tau_nqmab,
                left_uncertainties=delta_tau_nqmab,
                median=tau,
            ))
            s_weights.append(scaling_weights[user_m])

        s_weights = np.array(s_weights)
        tau_nqm = np.array(tau_nqm)
        delta_tau_nqm = np.array(delta_tau_nqm)
        if calibration:
            tau_dict[user_n] = lipschitz_resilient_mean(
                lipschitz=1/(8*W),
                voting_rights=s_weights,
                values=tau_nqm,
                left_uncertainties=delta_tau_nqm,
            )
            delta_tau_dict[user_n] = qr_uncertainty(
                lipschitz=1/(8*W),
                default_dev=1.0,
                voting_rights=s_weights,
                values=tau_nqm,
                left_uncertainties=delta_tau_nqm,
            )
        else:
            qr_med = qr_median(
                lipschitz=1/(8*W),
                voting_rights=s_weights,
                values=tau_nqm,
                left_uncertainties=delta_tau_nqm,
            )
            tau_dict[user_n] = qr_med
            delta_tau_dict[user_n] = qr_uncertainty(
                lipschitz=1/(8*W),
                default_dev=1.0,
                voting_rights=s_weights,
                values=tau_nqm,
                left_uncertainties=delta_tau_nqm,
                median=qr_med,
            )

    return pd.DataFrame(
        {
            "s": s_dict,
            "tau": tau_dict,
            "delta_s": delta_s_dict,
            "delta_tau": delta_tau_dict,
        }
    )
