import numpy as np
import pandas as pd

from tournesol.utils.constants import COMPARISON_MAX

R_MAX = COMPARISON_MAX  # Maximum score for a comparison in the input
ALPHA = 0.01  # Signal-to-noise hyperparameter


def compute_individual_score(scores: pd.DataFrame):
    """
    Computation of contributor scores and score uncertainties,
    based on their comparisons.

    At this stage, scores will not be normalized between contributors.
    """
    scores = scores[["entity_a", "entity_b", "score"]]
    l, k, L = calculate_lkL_from_scores(scores)
    K_diag = pd.DataFrame(
        data=np.diag(k.sum(axis=1) + ALPHA),
        index=k.index,
        columns=k.index,
    )
    K = K_diag.sub(k, fill_value=0)

    # theta_star = K^-1 * L
    theta_star_numpy = np.linalg.solve(K, L)
    theta_star = pd.Series(theta_star_numpy, index=L.index)

    # Compute uncertainties
    theta_star_ab = pd.DataFrame(
        np.subtract.outer(theta_star_numpy, theta_star_numpy),
        index=theta_star.index,
        columns=theta_star.index,
    )
    sigma2 = (1.0 + (np.nansum(k * (l - theta_star_ab) ** 2) / 2)) / len(scores)
    delta_star = pd.Series(np.sqrt(sigma2) / np.sqrt(np.diag(K)), index=K.index)

    result = pd.DataFrame(
        {
            "raw_score": theta_star,
            "raw_uncertainty": delta_star,
        }
    )
    result.index.name = "entity_id"
    return result


def calculate_lkL_from_scores(scores, filter=None):
    scores_sym = pd.concat(
        [
            scores,
            pd.DataFrame(
                {
                    "entity_a": scores.entity_b,
                    "entity_b": scores.entity_a,
                    "score": -1 * scores.score,
                }
            ),
        ]
    )

    # "Comparison tensor": matrix with all comparisons, values in [-R_MAX, R_MAX]
    r = scores_sym.pivot(index="entity_a", columns="entity_b", values="score")
    if filter:
        r = r.loc[filter]
    r_tilde = r / (1.0 + R_MAX)
    r_tilde2 = r_tilde**2

    # r.loc[a:b] is negative when a is prefered to b.
    l = -1.0 * r_tilde / np.sqrt(1.0 - r_tilde2)  # noqa: E741
    k = (1.0 - r_tilde2) ** 3

    L = k.mul(l).sum(axis=1)
    return l, k, L
