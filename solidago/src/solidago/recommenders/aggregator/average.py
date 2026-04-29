from solidago.poll import *
from .aggregator import Aggregator

class Average(Aggregator):
    def __call__(self, users: Users, entities: Entities, ballots: Scores) -> Entities:
        entities = entities.filters(ballots.keys("entity_name"))
        for entity in entities:
            subballots = ballots.filters(entity_name=entity.name)
            volumes = subballots.get_column("username").map(lambda u: users[u]["volume"])
            entities[entity.name, "weight"] = volumes * subballots.get_column("value") / volumes.sum()
        positive_weights = entities.get_column("weight") > 0
        entities = entities.assign(positive_weight=positive_weights)
        return entities.filters(positive_weights=True)
    