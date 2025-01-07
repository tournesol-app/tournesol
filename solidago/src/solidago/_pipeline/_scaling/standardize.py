import pandas as pd

from solidago.primitives import qr_standard_deviation
from solidago._state import *
from solidago._pipeline.base import StateFunction


class Standardize(StateFunction):
    def __init__(self, dev_quantile: float=0.9, lipschitz: float=0.1, error: float=1e-5):
        """ The scores are shifted so that their quantile zero_quantile equals zero
        
        Parameters
        ----------
        dev_quantile: float
        """
        self.dev_quantile = dev_quantile
        self.lipschitz = lipschitz
        self.error = error

    def __call__(self, entities: Entities, user_models: UserModels) -> UserModels:
        scores = user_models.score(entities).reorder_keys(["criterion", "username", "entity_name"])
        scales = ScaleDict(key_names=["criterion"]) # the same scale will apply to all users        
        for criterion in scores.get_set("criterion"):
            scores_df = scores.to_df()
            weights = 1 / scores_df.groupby("username")["scores"].transform("size")
            std_dev = qr_standard_deviation(
                lipschitz=self.lipschitz,
                values=scores_df["scores"].to_numpy(),
                quantile_dev=self.dev_quantile,
                voting_rights=weights.to_numpy(),
                left_uncertainties=scores_df["left_unc"].to_numpy(),
                right_uncertainties=scores_df["right_unc"].to_numpy(),
                default_dev=1.0,
                error=self.error,
            )
            scales[criterion] = (1 / std_dev, 0, 0, 0, 0, 0)
        
        return UserModels({
            username: ScaledModel(model, scales, note="standardize")
            for username, model in user_models
        })
