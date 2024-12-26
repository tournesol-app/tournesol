from solidago.state import Criterion, Criteria


class CriterionGenerator:
    def __call__(self, n_criteria: int) -> Criteria:
        return Criteria([ self.sample(criterion_id) for criterion_id in range(n_criteria) ])
    
    def sample(self, criterion_id):
        return Criterion(name=criterion_id)
        
    def __str__(self):
        return type(self).__name__
    
    def to_json(self):
        return (type(self).__name__, )


