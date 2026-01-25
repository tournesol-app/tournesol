import numpy as np
from numpy.typing import NDArray

from solidago.poll import *
from solidago.functions.aggregation.entity_criterion_wise import EntityCriterionWise


class Average(EntityCriterionWise):
    note: str="average"
    block_parallelization: bool = False
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
 
    def thread_function(self, 
        vrights: NDArray, 
        values: NDArray, 
        lefts: NDArray, 
        rights: NDArray
    ) -> tuple[float, float, float]:
        total_voting_rights = vrights.sum()
        if total_voting_rights == 0:
            return np.nan, np.inf, np.inf
        value = (values * vrights).sum() / total_voting_rights
        left = (lefts * vrights).sum() / total_voting_rights
        right = (rights * vrights).sum() / total_voting_rights
        return value, left, right
