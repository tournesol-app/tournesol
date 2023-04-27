import random
import numpy as np
import pandas as pd
from scipy.optimize import brentq

from tournesol.utils.constants import COMPARISON_MAX

R_MAX = COMPARISON_MAX  # Maximum score for a comparison in the input
ALPHA = 0.1  # Signal-to-noise hyperparameter

EPS = 1e-7

#    np.where(
#                 np.abs(theta) < 1,
#                 theta / 3,
#                 1/np.tanh(theta) - 1/theta 
#             )

def coordinate_optimize(r, theta, coord, precision):
    theta = theta.copy()

    r_ab = r[coord,:]
    indices = (~np.isnan(r_ab)).nonzero()
    r_ab = r_ab[indices]
    theta_b = theta[indices]

    def L_prime(theta_a):
        # theta[coord] = theta_a
        theta_ab = theta_a - theta_b
        result = ALPHA * theta_a + np.sum(
            np.where(
                np.abs(theta_ab) < EPS,
                theta_ab / 3,
                1/np.tanh(theta_ab) - 1/theta_ab,
            )
            + r_ab
        )
        return result

    theta_low = -5.
    while L_prime(theta_low) > 0:
        theta_low *= 2
    
    theta_up = 5.
    while L_prime(theta_up) < 0:
        theta_up *= 2

    theta_a = brentq(L_prime, theta_low, theta_up, xtol=precision)
    theta[coord] = theta_a
    return theta


def coordinate_descent(r):
    n_alternatives = len(r)
    unchanged = set()
    theta = np.zeros(n_alternatives)

    while len(unchanged) < n_alternatives:
        coord = random.choice(list(set(range(n_alternatives)) - unchanged))
        theta_new = coordinate_optimize(r, theta, coord, precision=EPS/10)
        diff = np.linalg.norm(theta-theta_new, ord=1)
        if diff < EPS:
            unchanged.add(coord)
        else:
            unchanged.clear()
        theta = theta_new

    return theta



def compute_individual_score(scores: pd.DataFrame):
    """
    Computation of contributor scores and score uncertainties,
    based on their comparisons.

    At this stage, scores will not be normalized between contributors.
    """
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

    r = scores_sym.pivot(index="entity_a", columns="entity_b", values="score") / R_MAX
    theta_star_numpy = coordinate_descent(r.values)
    theta_star = pd.Series(theta_star_numpy, index=r.index)


    # # Compute uncertainties
    # theta_star_ab = pd.DataFrame(
    #     np.subtract.outer(theta_star_numpy, theta_star_numpy),
    #     index=theta_star.index,
    #     columns=theta_star.index,
    # )
    # sigma2 = (1.0 + (np.nansum(k * (l - theta_star_ab) ** 2) / 2)) / len(scores)
    # delta_star = pd.Series(np.sqrt(sigma2) / np.sqrt(np.diag(K)), index=K.index)

    result = pd.DataFrame(
        {
            "raw_score": theta_star,
            "raw_uncertainty": 1.0,
        }
    )
    result.index.name = "entity_id"
    return result
