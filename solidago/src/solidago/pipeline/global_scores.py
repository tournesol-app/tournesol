import pandas as pd
import numpy as np

from solidago.resilient_primitives import QrDev, QrMed
from .parameters import PipelineParameters


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
        w = scores.voting_right
        theta = scores.score
        delta = scores.uncertainty
        rho = QrMed(W, w, theta, delta)
        rho_uncertainty = QrDev(W, 1, w, theta, delta, qr_med=rho)
        global_scores[entity_id] = {
            "score": rho,
            "uncertainty": rho_uncertainty,
            "n_contributors": len(scores),
        }

    result = pd.DataFrame.from_dict(global_scores, orient="index")
    result.index.name = "entity_id"
    return result.reset_index()
