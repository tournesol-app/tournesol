from typing import Any
from solidago.poll_functions.poll_function import PollFunction
from solidago.primitives.random import Distribution
from solidago import poll


class Entities(PollFunction):
    def __init__(self, 
        n_entities: int = 30, 
        distribution: Distribution | tuple[str, dict[str, Any]] | None = None
    ):
        self.n_entities = n_entities
        if distribution:
            self.distribution = Distribution.load(distribution)
    
    def sample_entity(self, entity_index: int) -> poll.Entity:
        vector = self.distribution.sample() if hasattr(self, "distribution") else None
        return poll.Entity(f"entity_{entity_index}", vector=vector)

    def __call__(self) -> poll.Entities:
        return poll.Entities([self.sample_entity(entity_index) for entity_index in range(self.n_entities)])

class AddColumn(PollFunction):
    def __init__(self, column: str, distribution: Distribution | tuple[str, dict[str, Any]]):
        self.column = column
        self.distribution = Distribution.load(distribution)
    
    def __call__(self, entities: poll.Entities) -> poll.Entities:
        kwargs = {self.column: self.distribution.sample(len(entities))}
        return entities.assign(**kwargs)