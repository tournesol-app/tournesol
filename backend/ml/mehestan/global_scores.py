import numpy as np
import pandas as pd

from ml.inputs import MlInput

from .primitives import BrMean, QrDev, QrMed, QrUnc

W = 20.0

SCALING_WEIGHT_SUPERTRUSTED = W
SCALING_WEIGHT_TRUSTED = 1.0
SCALING_WEIGHT_NONTRUSTED = 0.0

VOTE_WEIGHT_TRUSTED_PUBLIC = 1.0
VOTE_WEIGHT_TRUSTED_PRIVATE = 0.5

TOTAL_VOTE_WEIGHT_NONTRUSTED_DEFAULT = 2.0  # w_⨯,default
TOTAL_VOTE_WEIGHT_NONTRUSTED_FRACTION = 0.1  # f_⨯


# def get_user_scaling_weights():
#     values = (
#         User.objects.all()
#         .annotate(
#             scaling_weight=Case(
#                 When(
#                     pk__in=User.supertrusted_users(), then=SCALING_WEIGHT_SUPERTRUSTED
#                 ),
#                 When(pk__in=User.trusted_users(), then=SCALING_WEIGHT_TRUSTED),
#                 default=SCALING_WEIGHT_NONTRUSTED,
#             )
#         )
#         .values("scaling_weight", user_id=F("pk"))
#     )
#     return {u["user_id"]: u["scaling_weight"] for u in values}


def get_user_scaling_weights(ml_input: MlInput):
    ratings_properties = ml_input.get_ratings_properties()[
        ["user_id", "is_trusted", "is_supertrusted"]
    ]
    df = ratings_properties.groupby("user_id").first()
    df["scaling_weight"] = SCALING_WEIGHT_NONTRUSTED
    df["scaling_weight"].mask(df.is_trusted, SCALING_WEIGHT_TRUSTED, inplace=True)
    df["scaling_weight"].mask(
        df.is_supertrusted, SCALING_WEIGHT_SUPERTRUSTED, inplace=True
    )
    return df["scaling_weight"].to_dict()


def get_significantly_different_pairs(scores: pd.DataFrame):
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
    compute_uncertainties=False,
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

            # To check: is it correct to subtract s_nqmab?
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

            s = QrMed(1, 1, s_nqmab, delta_s_nqmab)
            s_nqm.append(s)
            delta_s_nqm.append(QrUnc(1, 1, 1, s_nqmab, delta_s_nqmab, qr_med=s))
            s_weights.append(scaling_weights[user_m])

        s_weights = np.array(s_weights)
        theta_inf = np.max(user_scores.score.abs())
        s_nqm = np.array(s_nqm)
        delta_s_nqm = np.array(delta_s_nqm)
        if compute_uncertainties:
            qr_med = QrMed(8 * W * theta_inf, s_weights, s_nqm - 1, delta_s_nqm)
            s_dict[user_n] = 1 + qr_med
            delta_s_dict[user_n] = QrUnc(
                8 * W * theta_inf, 1, s_weights, s_nqm - 1, delta_s_nqm, qr_med=qr_med
            )
        else:
            s_dict[user_n] = 1 + BrMean(
                8 * W * theta_inf, s_weights, s_nqm - 1, delta_s_nqm
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

        if compute_uncertainties:
            qr_med = QrMed(8 * W, s_weights, tau_nqm, delta_tau_nqm)
            tau_dict[user_n] = qr_med
            delta_tau_dict[user_n] = QrUnc(
                8 * W, 1, s_weights, tau_nqm, delta_tau_nqm, qr_med=qr_med
            )
        else:
            tau_dict[user_n] = BrMean(8 * W, s_weights, tau_nqm, delta_tau_nqm)

    return pd.DataFrame(
        {
            "s": s_dict,
            "tau": tau_dict,
            **(
                {"delta_s": delta_s_dict, "delta_tau": delta_tau_dict}
                if compute_uncertainties
                else {}
            ),
        }
    )


def get_scaling_for_supertrusted(ml_input: MlInput, individual_scores: pd.DataFrame):
    rp = ml_input.get_ratings_properties()
    rp.set_index(["user_id", "entity_id"], inplace=True)
    rp = rp[rp.is_supertrusted]
    df = individual_scores.join(rp, on=["user_id", "entity_id"], how="inner")
    return compute_scaling(df, ml_input=ml_input)


def get_global_scores(ml_input: MlInput, individual_scores: pd.DataFrame):
    if len(individual_scores) == 0:
        return pd.DataFrame(columns=["entity_id", "score", "uncertainty", "deviation"])

    supertrusted_scaling = get_scaling_for_supertrusted(ml_input, individual_scores)
    rp = ml_input.get_ratings_properties()

    non_supertrusted = rp["user_id"][~rp.is_supertrusted].unique()
    trusted_and_supertrusted = rp["user_id"][
        (rp.is_supertrusted) | (rp.is_trusted)
    ].unique()

    rp.set_index(["user_id", "entity_id"], inplace=True)
    df = individual_scores.join(rp, on=["user_id", "entity_id"], how="left")
    df["is_public"].fillna(False, inplace=True)
    df["is_trusted"].fillna(False, inplace=True)
    df["is_supertrusted"].fillna(False, inplace=True)

    df = df.join(supertrusted_scaling, on="user_id")
    df["s"].fillna(1, inplace=True)
    df["tau"].fillna(0, inplace=True)
    df["score"] = df["s"] * df["score"] + df["tau"]
    df["uncertainty"] *= df["s"]
    df.drop(["s", "tau"], axis=1, inplace=True)

    non_supertrusted_scaling = compute_scaling(
        df,
        ml_input=ml_input,
        users_to_compute=non_supertrusted,
        reference_users=trusted_and_supertrusted,
        compute_uncertainties=True,
    )

    df = df.join(non_supertrusted_scaling, on="user_id")
    df["s"].fillna(1, inplace=True)
    df["tau"].fillna(0, inplace=True)
    df["delta_s"].fillna(0, inplace=True)
    df["delta_tau"].fillna(0, inplace=True)
    df["uncertainty"] = (
        df["s"] * df["uncertainty"]
        + df["delta_s"] * df["score"].abs()
        + df["delta_tau"]
    )
    df["score"] = df["score"] * df["s"] + df["tau"]
    df.drop(["s", "tau", "delta_s", "delta_tau"], axis=1, inplace=True)

    df[
        "voting_weight"
    ] = 0  # Voting weight for non trusted users will be computed per entity
    df["voting_weight"].mask(
        (df.is_trusted) & (df.is_public), VOTE_WEIGHT_TRUSTED_PUBLIC, inplace=True
    )
    df["voting_weight"].mask(
        (df.is_trusted) & (~df.is_public), VOTE_WEIGHT_TRUSTED_PRIVATE, inplace=True
    )

    global_scores = {}
    for (entity_id, scores) in df.groupby("entity_id"):
        trusted_weight = scores["voting_weight"].sum()
        non_trusted_weight = (
            TOTAL_VOTE_WEIGHT_NONTRUSTED_DEFAULT
            + TOTAL_VOTE_WEIGHT_NONTRUSTED_FRACTION * trusted_weight
        )
        nb_non_trusted_public = (
            scores["is_public"] & (scores["voting_weight"] == 0)
        ).sum()
        nb_non_trusted_private = (
            ~scores["is_public"] & (scores["voting_weight"] == 0)
        ).sum()

        if (nb_non_trusted_private > 0) or (nb_non_trusted_public > 0):
            scores["voting_weight"].mask(
                scores["is_public"] & (scores["voting_weight"] == 0),
                min(
                    VOTE_WEIGHT_TRUSTED_PUBLIC,
                    2
                    * non_trusted_weight
                    / (2 * nb_non_trusted_public + nb_non_trusted_private),
                ),
                inplace=True,
            )
            scores["voting_weight"].mask(
                ~scores["is_public"] & (scores["voting_weight"] == 0),
                min(
                    VOTE_WEIGHT_TRUSTED_PRIVATE,
                    non_trusted_weight
                    / (2 * nb_non_trusted_public + nb_non_trusted_private),
                ),
                inplace=True,
            )

        w = scores.voting_weight
        theta = scores.score
        delta = scores.uncertainty
        rho = QrMed(2 * W, w, theta, delta)
        rho_uncertainty = QrUnc(2 * W, 1, w, theta, delta, qr_med=rho)
        rho_deviation = QrDev(2 * W, 1, w, theta, delta, qr_med=rho)
        global_scores[entity_id] = {
            "score": rho,
            "uncertainty": rho_uncertainty,
            "deviation": rho_deviation,
        }

    if len(global_scores) == 0:
        return pd.DataFrame(columns=["entity_id", "score", "uncertainty", "deviation"])

    result = pd.DataFrame.from_dict(global_scores, orient="index")
    result.index.name = "entity_id"
    return result.reset_index()
