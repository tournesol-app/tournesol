import random
import numpy as np
import pandas as pd
from numba import njit

from ml.optimize import brentq
from tournesol.utils.constants import COMPARISON_MAX


R_MAX = COMPARISON_MAX  # Maximum score for a comparison in the input
ALPHA = 0.1  # Signal-to-noise hyperparameter

EPSILON = 1e-5


@njit
def L_prime(theta_a, theta_b, r_ab):
    theta_ab = theta_a - theta_b
    return ALPHA * theta_a + np.sum(
        np.where(
            np.abs(theta_ab) < EPSILON,
            theta_ab / 3,
            1 / np.tanh(theta_ab) - 1 / theta_ab,
        )
        + r_ab
    )


@njit
def Delta_theta(theta_ab):
    return np.where(
        np.abs(theta_ab) < EPSILON,
        1 / 3 - 1 / 15 * theta_ab**2,
        1 - (1 / np.tanh(theta_ab)) ** 2 + 1 / theta_ab**2,
    ).sum() ** (-0.5)


@njit
def coordinate_optimize(r_ab, theta_b, precision):
    theta_low = -5.0
    while L_prime(theta_low, theta_b, r_ab) > 0:
        theta_low *= 2

    theta_up = 5.0
    while L_prime(theta_up, theta_b, r_ab) < 0:
        theta_up *= 2

    return brentq(L_prime, theta_low, theta_up, args=(theta_b, r_ab), xtol=precision)


def get_random_coordinate(n, exclude: set):
    if len(exclude) < int(n * 0.95):
        while True:
            coord = random.randint(0, n - 1)
            if coord not in exclude:
                return coord
    return random.choice([i for i in range(n) if i not in exclude])


def coordinate_descent(r):
    n_alternatives = len(r)
    unchanged = set()

    theta = np.zeros(n_alternatives)
    coord_to_indices = {}

    while len(unchanged) < n_alternatives:
        coord = get_random_coordinate(n_alternatives, exclude=unchanged)
        if coord not in coord_to_indices:
            r_ab = r[coord, :]
            indices = (~np.isnan(r_ab)).nonzero()
            coord_to_indices[coord] = (indices, r_ab[indices])

        old_theta_a = theta[coord]
        indices, r_ab = coord_to_indices[coord]
        theta_b = theta[indices]
        new_theta_a = coordinate_optimize(r_ab, theta_b, precision=EPSILON / 10)
        theta[coord] = new_theta_a
        if abs(new_theta_a - old_theta_a) < EPSILON:
            unchanged.add(coord)
        else:
            unchanged.clear()

    return theta, coord_to_indices


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
    theta_star_numpy, coord_to_indices = coordinate_descent(r.values)

    delta_star_numpy = np.zeros(len(theta_star_numpy))
    for idx in range(len(theta_star_numpy)):
        indices, _r_ab = coord_to_indices[idx]
        delta_star_numpy[idx] = Delta_theta(theta_star_numpy[indices])

    result = pd.DataFrame(
        {
            "raw_score": theta_star_numpy,
            "raw_uncertainty": delta_star_numpy,
        },
        index=r.index,
    )
    result.index.name = "entity_id"
    return result


# if __name__ == "__main__":
    # from ml.inputs import MlInputFromPublicDataset
    # ml_input = MlInputFromPublicDataset("https://api.tournesol.app/exports/all/")
    # comp = ml_input.get_comparisons(user_id=116, criteria="largely_recommended")
    # res = compute_individual_score(comp)
    # print(res.sort_values("raw_score", ascending=False))
