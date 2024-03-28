import numpy as np
import pandas as pd

from solidago.voting_rights import AffineOvertrust


def compute_voting_rights(
    trust_scores: np.ndarray,
    privacy_penalties: np.ndarray,
    over_trust_bias: float,
    over_trust_scale: float,
) -> np.ndarray:
    affine_overtrust = AffineOvertrust(
        min_overtrust=over_trust_bias,
        overtrust_ratio=over_trust_scale,
    )
    trust_scores_series = pd.Series(trust_scores)
    privacy_weights = pd.Series(privacy_penalties, index=trust_scores_series.index)
    (voting_rights, _, _, _) = affine_overtrust.compute_entity_voting_rights(
        trust_scores_series,
        privacy_weights
    )
    return voting_rights.to_numpy()
