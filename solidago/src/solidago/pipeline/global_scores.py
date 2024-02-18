from typing import Literal, List, get_args

import pandas as pd
import numpy as np

from solidago.primitives import qr_uncertainty, qr_median
from solidago.voting_rights import compute_voting_rights
from .parameters import PipelineParameters


ScoreMode = Literal["default", "trusted_only", "all_equal"]
ALL_SCORE_MODES: List[ScoreMode] = list(get_args(ScoreMode))


def add_voting_rights(
    ratings_properties_df: pd.DataFrame,
    params: PipelineParameters,
    score_mode: ScoreMode = "default",
):
    """
    Add a "voting_right" column to the ratings_df DataFrame

    Parameters
    ----------
    - ratings_properties_df:
        DataFrame of ratings. All ratings must be on the same criteria and the df must have
        columns: user_id, entity_id, trust_score, is_public
    """
    ratings_df = ratings_properties_df.copy(deep=True)
    ratings_df["voting_right"] = 0.0
    ratings_df["privacy_penalty"] = ratings_df.is_public.map(
        {
            True: params.vote_weight_public_ratings,
            False: params.vote_weight_private_ratings,
        }
    )
    if score_mode == "trusted_only":
        ratings_df = ratings_df[ratings_df["trust_score"] >= 0.8]
        ratings_df["voting_right"] = 1
    elif score_mode == "all_equal":
        ratings_df["voting_right"] = 1
    elif score_mode == "default":
        # trust score would be possibly None (NULL) when new users are created and when
        # computation of trust scores fail for any reason (e.g. no user pre-trusted)
        ratings_df.trust_score.fillna(0.0, inplace=True)
        for (_, ratings_group) in ratings_df.groupby("entity_id"):
            ratings_df.loc[ratings_group.index, "voting_right"] = compute_voting_rights(
                ratings_group.trust_score.to_numpy(),
                ratings_group.privacy_penalty.to_numpy(),
                over_trust_bias=params.over_trust_bias,
                over_trust_scale=params.over_trust_scale,
            )
    else:
        raise ValueError(f"Unknown score mode '{score_mode}'")

    return ratings_df


def get_squash_function(params: PipelineParameters):
    def squash(x):
        return params.max_squashed_score * x / (
            np.sqrt(1 + x * x)
        )
    return squash


def aggregate_scores(scaled_scores: pd.DataFrame, W: float):
    if len(scaled_scores) == 0:
        return pd.DataFrame(
            columns=["entity_id", "score", "uncertainty", "deviation", "n_contributors"]
        )

    global_scores = {}
    for (entity_id, scores) in scaled_scores.groupby("entity_id"):
        w = scores.voting_right.to_numpy()
        theta = scores.score.to_numpy()
        delta = scores.uncertainty.to_numpy()
        rho = qr_median(
            lipschitz=1/W,
            values=theta,
            voting_rights=w,
            left_uncertainties=delta,
        )
        rho_uncertainty = qr_uncertainty(
            lipschitz=1/W,
            values=theta,
            voting_rights=w,
            left_uncertainties=delta,
            median=rho,
        )
        global_scores[entity_id] = {
            "score": rho,
            "uncertainty": rho_uncertainty,
            "n_contributors": len(scores),
        }

    result = pd.DataFrame.from_dict(global_scores, orient="index")
    result.index.name = "entity_id"
    return result.reset_index()
