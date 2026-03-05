from solidago.poll import *
from solidago.poll_functions.poll_function import PollFunction


class SimpleComparisonStats(PollFunction):
    def fn(self, comparisons: Comparisons) -> Comparisons:
        return comparisons.add_columns(
            left_first=self.left_first(comparisons),
            right_first=self.right_first(comparisons),
            multiple_criteria=self.multiple_criteria(comparisons),
            all_criteria=self.all_criteria(comparisons),
        )
    
    def left_first(self, comparisons: Comparisons) -> list[bool]:
        """ Whether a comparison is the first of left entity by user """
        raise NotImplemented # TODO
    
    def right_first(self, comparisons: Comparisons) -> list[bool]:
        """ Whether a comparison is the first of right entity by user """
        raise NotImplemented # TODO
    
    def multiple_criteria(self, comparisons: Comparisons) -> list[bool]:
        raise NotImplemented # TODO
    
    def all_criteria(self, comparisons: Comparisons) -> list[bool]:
        raise NotImplemented # TODO