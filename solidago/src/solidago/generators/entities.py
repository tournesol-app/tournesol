from typing import Any
from solidago.poll_functions.poll_function import PollFunction
from solidago.primitives.random import Distribution
from solidago import poll


class New(PollFunction):
    def __init__(self, 
        n_entities: int = 30, 
        distribution: Distribution | tuple[str, dict[str, Any]] | None = None
    ):
        import solidago
        self.n_entities = n_entities
        if distribution:
            distribution = solidago.load(distribution, solidago.random)
            assert isinstance(distribution, solidago.primitives.random.Distribution)
            self.distribution = distribution
    
    def sample_entity(self, entity_index: int) -> poll.Entity:
        vector = self.distribution.sample() if hasattr(self, "distribution") else None
        return poll.Entity(f"entity_{entity_index}", vector=vector)

    def fn(self) -> poll.Entities:
        return poll.Entities([self.sample_entity(entity_index).series for entity_index in range(self.n_entities)])

class AddColumn(PollFunction):
    def __init__(self, column: str, distribution: Distribution | tuple[str, dict[str, Any]]):
        import solidago
        self.column = column
        self.distribution = solidago.load(distribution, solidago.random)
    
    def fn(self, entities: poll.Entities) -> poll.Entities:
        kwargs = {self.column: self.distribution.sample(len(entities))}
        return entities.assign(**kwargs)