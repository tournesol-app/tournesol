"""
Computation of Contributors’ individual raw scores
based on Continuous Bradley-Terry model (CBT)
using coordinate descent.
"""
import random
from typing import Tuple, Callable

import numpy as np
import pandas as pd
from numba import njit

from solidago.comparisons_to_scores.base import ComparisonsToScoresAlgorithm
from solidago.solvers.optimize import brentq, SignChangeIntervalNotFoundError


DEFAULT_ALPHA = 0.20  # Signal-to-noise hyperparameter
EPSILON = 1e-5


@njit
def contributor_loss_partial_derivative(theta_a, theta_b, r_ab, alpha):
    theta_ab = theta_a - theta_b
    return alpha * theta_a + np.sum(
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


HIGH_LIKELIHOOD_RANGE_THRESHOLD = 1


@njit
def translated_function(x, f, translation):
    """Returns the function x => f(x) - translation"""
    return f(x) - translation

def get_high_likelihood_range(
    log_likelihood: Callable,
    maximum_a_posteriori: float,
    threshold: float = HIGH_LIKELIHOOD_RANGE_THRESHOLD,
) -> Tuple[float, float]:
    """
    Find a root of a function in a bracketing interval using Brent's method
    adapted from Scipy's brentq.
    Uses the classic Brent's method to find a zero of the function `f` on
    the sign changing interval [a , b].
    `f` must be jitted via numba.
    Parameters
    ----------
    likelihood_function:
        Python function returning a number. `f` must be continuous and concave.
    maximum_a_posteriori:
        The high liklihood position selected as most likely based on the prior
        distribution and the observed likelihood
    threshold:
        The threshold used to compute the high likelihood range. The range will
        be the interval with where we have
        log_likelihood > log_likelihood(maximum_a_posteriori) - threshold
        The threshold must be strictly positive.
    Returns
    -------
    interval:
        A tuple of float representing an interval containing the
        maximum_a_posteriori.
    """
    if threshold <= 0:
        raise ValueError("`threshold` must be strictly positive")
    min_log_likelihood =  log_likelihood(maximum_a_posteriori) - threshold

    lower_bound, upper_bound = 0., 0.
    try:
        lower_bound = brentq(translated_function, a=maximum_a_posteriori-1, b=maximum_a_posteriori, search_b=False, args=(log_likelihood, min_log_likelihood))
    except SignChangeIntervalNotFoundError:
        lower_bound = -np.inf
    try: 
        upper_bound = brentq(translated_function, a=maximum_a_posteriori, b=maximum_a_posteriori+1, search_a=False, args=(log_likelihood, min_log_likelihood))
    except SignChangeIntervalNotFoundError:
        upper_bound = np.inf

    return lower_bound, upper_bound


@njit
def coordinate_optimize(r_ab, theta_b, precision, alpha):
    return brentq(
        contributor_loss_partial_derivative,
        args=(theta_b, r_ab, alpha),
        xtol=precision,
    )


class ContinuousBradleyTerry(ComparisonsToScoresAlgorithm):
    def __init__(self, r_max, alpha=DEFAULT_ALPHA):
        """
        Initialize Continous Bradley Terry (CBT) to compute individual scores

        Parameters
        ----------
        r_max: Maximum absolute score of a comparison
        alpha: Regularization term
        """
        self.alpha = alpha
        self.r_max = r_max

    def coordinate_descent(self, coord_to_subset, initial_scores):
        n_alternatives = len(coord_to_subset)
        unchanged = set()
        to_pick = []

        def pick_next_coordinate():
            nonlocal to_pick
            if len(to_pick) == 0:
                to_pick = list(range(n_alternatives))
                random.shuffle(to_pick)
            return to_pick.pop()

        theta = initial_scores
        while len(unchanged) < n_alternatives:
            coord = pick_next_coordinate()
            if coord in unchanged:
                continue
            indices, r_ab = coord_to_subset[coord]
            old_theta_a = theta[coord]
            theta_b = theta[indices]
            new_theta_a = coordinate_optimize(
                r_ab, theta_b, precision=EPSILON / 10, alpha=self.alpha
            )
            theta[coord] = new_theta_a
            if abs(new_theta_a - old_theta_a) < EPSILON:
                unchanged.add(coord)
            else:
                unchanged.clear()
        return theta

    def compute_individual_scores(self, comparison_scores: pd.DataFrame, initial_entity_scores=None):
        comparison_scores = comparison_scores[["entity_a", "entity_b", "score"]]
        scores_sym = (
            pd.concat(
                [
                    comparison_scores,
                    pd.DataFrame(
                        {
                            "entity_a": comparison_scores.entity_b,
                            "entity_b": comparison_scores.entity_a,
                            "score": -1 * comparison_scores.score,
                        }
                    ),
                ]
            )
            .set_index(["entity_a", "entity_b"])
            .sort_index()
        )
        entities_index = scores_sym.index.get_level_values("entity_a").unique()
        coord_to_subset = {}
        for (coord, (_a, group)) in enumerate(scores_sym.groupby(level="entity_a", sort=False)):
            r_ab = group["score"].to_numpy()
            indices = entities_index.get_indexer(group.index.get_level_values("entity_b"))
            coord_to_subset[coord] = (indices, r_ab)

        if initial_entity_scores is None:
            initial_scores = np.zeros(len(entities_index))
        else:
            initial_scores = pd.Series(initial_entity_scores, index=entities_index)
            initial_scores.fillna(0.0, inplace=True)
            initial_scores = initial_scores.to_numpy()
        theta_star_numpy = self.coordinate_descent(coord_to_subset, initial_scores=initial_scores)
        delta_star_numpy = np.zeros(len(theta_star_numpy))
        for idx_a in range(len(theta_star_numpy)):
            indices_b, _r_ab = coord_to_subset[idx_a]
            delta_star_numpy[idx_a] = Delta_theta(theta_star_numpy[idx_a] - theta_star_numpy[indices_b])

        result = pd.DataFrame(
            {
                "raw_score": theta_star_numpy,
                "raw_uncertainty": delta_star_numpy,
            },
            index=entities_index,
        )
        result.index.name = "entity_id"
        return result

    def get_metadata(self) -> dict:
        return {
            "algorithm_name": "continuous_bradley_terry",
            "parameters": {
                "R_MAX": self.r_max,
                "ALPHA": self.alpha,
            },
        }
