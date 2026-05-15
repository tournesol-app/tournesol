import numpy as np
from numpy.typing import NDArray

from solidago.poll import *
from solidago.functions.aggregation.entity_criterion_wise import EntityCriterionWise


class Sum(EntityCriterionWise):
    note: str="sum"
    parallelize: bool = False

    def thread_function(self, 
        vrights: NDArray[np.float64], 
        values: NDArray[np.float64], 
        left_uncs: NDArray[np.float64], 
        right_uncs: NDArray[np.float64],
    ) -> tuple[float, float, float]:
        assert len(vrights) == len(values) == len(left_uncs) == len(right_uncs)
        return (values * vrights).sum(), (left_uncs * vrights).sum(), (right_uncs * vrights).sum()
