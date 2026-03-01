import numpy as np
from numpy.typing import NDArray

from solidago.poll import *
from solidago.poll_functions.aggregation.entity_criterion_wise import EntityCriterionWise


class Average(EntityCriterionWise):
    note: str="average"
    block_parallelization: bool = False
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
 
    def thread_function(self, 
        vrights: NDArray[np.float64], 
        values: NDArray[np.float64], 
        left_uncs: NDArray[np.float64], 
        right_uncs: NDArray[np.float64],
    ) -> tuple[float, float, float]:
        assert len(vrights) == len(values) == len(left_uncs) == len(right_uncs)
        print((vrights, values, left_uncs, right_uncs))
        total_voting_rights = vrights.sum()
        if total_voting_rights == 0:
            return np.nan, np.inf, np.inf
        value = (values * vrights).sum() / total_voting_rights
        left_unc = (left_uncs * vrights).sum() / total_voting_rights
        right_unc = (right_uncs * vrights).sum() / total_voting_rights
        return value, left_unc, right_unc
