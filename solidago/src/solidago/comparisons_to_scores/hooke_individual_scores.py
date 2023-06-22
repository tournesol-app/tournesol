import numpy as np
import pandas as pd

from .base import ComparisonsToScoresAlgorithm

DEFAULT_ALPHA = 1.0  # Signal-to-noise hyperparameter


class HookeIndividualScores(ComparisonsToScoresAlgorithm):
    def __init__(self, r_max, alpha=DEFAULT_ALPHA):
        """
        Initialize in Matrix Inversion algorithm

        Parameters
        ----------
        r_max: maximum absolute score of a comparison
        alpha: Signal-to-noise hyperparameter, regularization term
        """
        self.alpha = alpha
        self.r_max = r_max

    def compute_individual_scores(
        self, comparison_scores: pd.DataFrame, initial_entity_scores=None
    ):
        scores = comparison_scores[["entity_a", "entity_b", "score"]]
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

        r_tilde = r / (1.0 + self.r_max)
        r_tilde2 = r_tilde**2

        # r.loc[a:b] is negative when a is prefered to b.
        l = -1.0 * r_tilde / np.sqrt(1.0 - r_tilde2)  # noqa: E741
        k = (1.0 - r_tilde2) ** 3

        L = k.mul(l).sum(axis=1)
        K_diag = pd.DataFrame(
            data=np.diag(k.sum(axis=1) + self.alpha),
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

    def get_metadata(self) -> dict:
        return {
            "algorithm_name": "matrix_inversion",
            "parameters": {
                "R_MAX": self.r_max,
                "ALPHA": self.alpha,
            }
        }
