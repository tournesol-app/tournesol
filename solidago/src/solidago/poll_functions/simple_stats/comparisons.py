from typing import Hashable
from numpy.typing import NDArray
import numpy as np

from solidago.poll import *
from solidago.poll_functions.poll_function import PollFunction


class SimpleComparisonStats(PollFunction):
    def __init__(self, 
        main_criterion: str | None = None, 
        criteria: set[str] | None = None, 
        max_workers: int | None = None
    ):
        super().__init__(max_workers)
        self.main_criterion = main_criterion
        self.criteria = criteria

    def fn(self, users: Users, ratings: Ratings, comparisons: Comparisons) -> Comparisons:
        if self.criteria is None:
            criteria = {str(c) for c in comparisons.keys("criterion") | ratings.keys("criterion")}
        else:
            criteria = self.criteria
        left_firsts, right_firsts = self.firsts(comparisons)
        return comparisons.add_columns(
            left_first=left_firsts,
            right_first=right_firsts,
            first_value=self.first_values(comparisons),
            multiple_criteria=self.multiple_criteria(comparisons),
            all_criteria=self.all_criteria(comparisons, criteria),
            user_trust=self.user_trusts(users, comparisons)
        )
    
    def firsts(self, comparisons: Comparisons) -> tuple[list[bool], list[bool]]:
        """ Whether a comparison is the first time the left/right entity was evaluated by user """
        left_firsts, right_firsts = list(), list()
        past_evaluations: set[tuple[str, str]] = set() # username, entity_name
        
        for c in comparisons:
        
            if self.main_criterion is not None and c["criterion"] != self.main_criterion:
                left_firsts.append(False)
                right_firsts.append(False)
                continue
        
            for entity_name, firsts in zip((c["left_name"], c["right_name"]), (left_firsts, right_firsts)):
                if (c["username"], entity_name) in past_evaluations:
                    firsts.append(False)
                else:
                    past_evaluations.add((c["username"], entity_name))
                    firsts.append(True)

        return left_firsts, right_firsts
    
    def first_values(self, comparisons: Comparisons) -> list[float]:
        first_values = list()
        for c in comparisons:
            if c["left_first"] and not c["right_first"]:
                first_values.append(c["value"])
            elif c["right_first"] and not c["left_first"]:
                first_values.append(- c["value"])
            else:
                first_values.append(np.nan)
        return first_values
    
    def multiple_criteria(self, comparisons: Comparisons) -> list[bool]:
        multiple_criteria_list = list()
        for c in comparisons:
            kwargs = dict(username=c["username"], left_name=c["left_name"], right_name=c["right_name"])
            criteria = comparisons.filters(**kwargs).keys("criterion")
            multiple_criteria_list.append(len(criteria) > 1)
        return multiple_criteria_list
    
    def all_criteria(self, comparisons: Comparisons, criteria: set[str]) -> list[bool]:
        has_all_criteria_list = list()
        for c in comparisons:
            kwargs = dict(username=c["username"], left_name=c["left_name"], right_name=c["right_name"])
            criteria = {str(c) for c in comparisons.filters(**kwargs).keys("criterion")}
            has_all_criteria_list.append(criteria == self.criteria)
        return has_all_criteria_list
    
    def user_trusts(self, users: Users, comparisons: Comparisons) -> NDArray[np.float64]:
        users = users.filters(comparisons.get_column("username"))
        return users.get_column("trust").to_numpy(np.float64)