import numpy as np
import pandas as pd

R_MAX = 10
ALPHA = 0.01


def compute_individual_score(scores):
    scores = scores[["entity_a", "entity_b", "score"]]
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

    r = scores_sym.pivot(index="entity_a", columns="entity_b", values="score")

    r_tilde = r / (1.0 + R_MAX)
    r_tilde2 = r_tilde ** 2

    # r.loc[a:b] is negative when a is prefered to b.
    l = -1.0 * r_tilde / np.sqrt(1.0 - r_tilde2)  # noqa: E741
    k = (1.0 - r_tilde2) ** 3

    L = k.mul(l).sum(axis=1)
    K_diag = pd.DataFrame(
        data=np.diag(k.sum(axis=1) + ALPHA),
        index=k.index,
        columns=k.index,
    )
    K = K_diag.sub(k, fill_value=0)

    # theta_star = K^-1 * L
    theta_star = pd.Series(np.linalg.solve(K, L), index=L.index)

    # Compute uncertainties
    theta_star_numpy = theta_star.to_numpy()
    theta_star_ab = pd.DataFrame(
        np.subtract.outer(theta_star_numpy, theta_star_numpy),
        index=theta_star.index,
        columns=theta_star.index,
    )
    sigma2 = (1.0 + (np.nansum(k * (l - theta_star_ab) ** 2) / 2)) / len(scores)
    delta_star = pd.Series(np.sqrt(sigma2) / np.sqrt(np.diag(K)), index=K.index)

    result = pd.DataFrame(
        {
            "score": theta_star,
            "uncertainty": delta_star,
        }
    )
    result.index.name = "entity_id"
    return result
