import pandas as pd
import numpy as np

from .standardized_qr_quantile import StandardizedQrQuantile

from solidago.voting_rights import VotingRights
from solidago.scoring_model import ScoringModel, DirectScoringModel, ScaledScoringModel


class StandardizedQrMedian(StandardizedQrQuantile):
    def __init__(self, dev_quantile=0.9, lipschitz=0.1, error=1e-5):
        """ Standardize scores so that only a fraction 1 - dev_quantile
        of the scores is further than 1 away from the median,
        and then run qr_median to aggregate the scores.
        
        Parameters
        ----------
        qtl_std_dev: float
        lipschitz: float
        error: float
        """
        super().__init__(0.5, dev_quantile, lipschitz, error)
     
    def to_json(self):
        return type(self).__name__, dict(
            dev_quantile=self.dev_quantile, lipschitz=self.lipschitz, error=self.error
        )

    def __str__(self):
        prop_names = ["dev_quantile", "lipschitz", "error"]
        prop = ", ".join([f"{p}={getattr(self, p)}" for p in prop_names])
        return f"{type(self).__name__}({prop})"
