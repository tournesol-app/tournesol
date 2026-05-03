import numpy as np

from solidago.poll import *
from solidago.recommenders.sampler import Sampler
from solidago.recommenders.sampler.pivot_scheduler import PivotScheduler


class Tille(Sampler):
    def __init__(self, pivot_scheduler: PivotScheduler | tuple[str, dict]):
        import solidago, solidago.recommenders.sampler.pivot_scheduler as m
        self.pivot_scheduler = solidago.load(pivot_scheduler, m, PivotScheduler)

    def eliminate(self, poll: Poll, entities: Entities) -> tuple[Entity, Entities]:
        """ Returns eliminated entity, and weight-updated entities """
        entities = entities\
            .assign(candidate=entities.get_column("weight") > 0)\
            .filters(positive=True)
        e, f = self.pivot_scheduler(poll, entities)
        total_weight = e["weight"] + f["weight"]
        e_win_probability = e["weight"] / total_weight
        winner, loser = (e, f) if np.random.random() <= e_win_probability else (f, e)
        entities[winner.name, "weight"] = total_weight
        entities[loser.name, "weight"] = 0
        return loser, entities

    def __call__(self, poll: Poll, limit: int) -> Entities:
        entities = poll.entities\
            .assign(candidate=poll.entities.get_column("weight") > 0)\
            .filters(positive=True)\
            .assign(rank=1)
        for i in range(len(entities)):
            loser, entities = self.eliminate(poll, entities)
            entities[loser.name, "rank"] = len(entities) - i
        return entities.sort_by("rank").head(limit)
    