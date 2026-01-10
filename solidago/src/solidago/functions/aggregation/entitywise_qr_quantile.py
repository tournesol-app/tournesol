from functools import cached_property
from typing import Callable
import numpy as np
from numpy import ndarray as NPArr

from solidago.primitives.lipschitz import qr_quantile, qr_uncertainty
from solidago.poll import *
from solidago.functions.aggregation.entity_criterion_wise import EntityCriterionWise


class EntitywiseQrQuantile(EntityCriterionWise):
    note: str="entitywise_qr_quantile"
    
    def __init__(self, quantile: float=0.2, lipschitz: float=0.1, error: float=1e-5, *args, **kwargs):
        """ Aggregates scores using the quadratically regularized quantile,
        for each entity and each criterion.
        
        Parameters
        ----------
        quantile: float
        lipschitz: float
        error: float
        """
        super().__init__(*args, **kwargs)
        self.quantile = quantile
        self.lipschitz = lipschitz
        self.error = error

    @cached_property
    def thread_function(self) -> Callable:
        def fn(vrights: NPArr, values: NPArr, lefts: NPArr, rights: NPArr) -> tuple[float, float, float]:
            if len(values) == 0:
                return np.nan, np.inf, np.inf
            kwargs = dict(lipschitz=self.lipschitz, error=self.error, voting_rights=vrights)
            kwargs |= dict(values=values, left_uncertainties=lefts, right_uncertainties=rights)
            quantile_score = qr_quantile(quantile=self.quantile, **kwargs)
            median = quantile_score if self.quantile == 0.5 else None
            uncertainty = qr_uncertainty(default_dev=1.0, median=median, **kwargs)
            return quantile_score, uncertainty, uncertainty
        return fn
