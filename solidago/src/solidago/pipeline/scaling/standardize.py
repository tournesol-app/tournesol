import pandas as pd

from solidago.primitives import qr_standard_deviation
from solidago.state import *
from solidago.pipeline.base import StateFunction


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
        scores_df = user_models.score(entities).reorder_keys(["criterion"]).to_df()
        multiplicator2scale = lambda multiplicator: (multiplicator, 0, 0, 0, 0, 0)
        scalings = dict()
        
        for criterion in scores_df.get_set("criterion"):
            weights = 1 / df.groupby("username")["scores"].transform("size")
            std_dev = qr_standard_deviation(
                lipschitz=self.lipschitz,
                values=df["scores"].to_numpy(),
                quantile_dev=self.dev_quantile,
                voting_rights=weights.to_numpy(),
                left_uncertainties=df["left_uncertainties"].to_numpy(),
                right_uncertainties=df["right_uncertainties"].to_numpy(),
                default_dev=1.0,
                error=self.error,
            )
            scalings[criterion] = multiplicator2scale(1 / std_dev)
        
        return UserModels({
            username: MultiScaledModel(model, scalings)
            for username, model in user_models
        })
