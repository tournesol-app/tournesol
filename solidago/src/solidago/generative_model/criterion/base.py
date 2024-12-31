from solidago.state import *


class CriterionGenerator:
    criteria_cls: type=Criteria
    
    def __init__(self, n_criteria: int=0):
        assert isinstance(n_criteria, int) and n_criteria >= 0
        self.n_criteria = n_criteria
    
    def __call__(self, state: State) -> None:
        if n_criteria == 0:
            return None
        state.criteria = self.criteria_cls([ self.sample(c) for c in range(n_criteria) ])
    
    def sample(self, criterion):
        return self.criteria_cls.series_cls(name=criterion)
        
