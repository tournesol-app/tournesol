from solidago.poll import *
from .aggregator import Aggregator

class Sum(Aggregator):
    def __call__(self, poll: Poll, councillors: Users, ballots: Scores) -> Entities:
        entities = poll.entities.filters(ballots.keys("entity_name"))
        for entity in entities:
            subballots = ballots.filters(entity_name=entity.name)
            volumes = subballots.get_column("username").map(lambda u: councillors[u]["volume"])
            entities[entity.name, "weight"] = volumes * subballots.get_column("value")
        positive_weights = entities.get_column("weight") > 0
        entities = entities.assign(positive_weight=positive_weights)
        return entities.filters(positive_weights=True)
    