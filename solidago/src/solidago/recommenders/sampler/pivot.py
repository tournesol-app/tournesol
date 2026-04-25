import numpy as np
from solidago.poll import *
from solidago.recommenders.representatives.weights_compute import WeightsCompute
from src.solidago.recommenders.sampler.pivot_scheduler.pivot_scheduler import PivotScheduler


class Pivot:
    def __init__(self,
        weights_compute: WeightsCompute | tuple[str, dict],
        pivot_scheduler: PivotScheduler | tuple[str, dict],
        shuffle: bool = True,
    ):
        import solidago
        import solidago.recommenders.representatives.weights_compute as weights_compute_module
        weights_compute = solidago.load(weights_compute, weights_compute_module)
        assert isinstance(weights_compute, WeightsCompute)
        self.weights_compute = weights_compute
        import src.solidago.recommenders.sampler.pivot_scheduler as pivot_scheduler_module
        pivot_scheduler = solidago.load(pivot_scheduler, pivot_scheduler_module)
        assert isinstance(pivot_scheduler, PivotScheduler)
        self.pivot_scheduler = pivot_scheduler
        self.shuffle = shuffle

    def pivot(self, entities: Entities, limit: int) -> Entities:
        while len(entities) > limit:
            e, f = self.pivot_scheduler(entities)
            total_weight = e["weight"] + f["weight"]
            e_win_probability = e["weight"] / total_weight
            win, loss = (e, f) if np.random.random() <= e_win_probability else (f, e)
            entities[win.name, "weight"] = total_weight
            entities = entities.drop(loss.name)
        return entities

    def __call__(self, poll: Poll, username: str, limit: int, cursor: str | None = None) -> Entities:
        entities = self.weights_compute(poll, username, "weight", cursor)
        return self.pivot(entities, limit).shuffle(self.shuffle)
    