from functools import cached_property
from typing import Callable
import numpy as np
from numpy import ndarray as NPArr

from solidago.poll import *
from solidago.functions.aggregation.entity_criterion_wise import EntityCriterionWise


class Average(EntityCriterionWise):
    note: str="average"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @cached_property    
    def thread_function(self) -> Callable:
        return Average.fn

    def fn(vrights: NPArr, values: NPArr, lefts: NPArr, rights: NPArr) -> tuple[float, float, float]:
        total_voting_rights = vrights.sum()
        if total_voting_rights == 0:
            return np.nan, np.inf, np.inf
        value = (values * vrights).sum() / total_voting_rights
        left = (lefts * vrights).sum() / total_voting_rights
        right = (rights * vrights).sum() / total_voting_rights
        return value, left, right
