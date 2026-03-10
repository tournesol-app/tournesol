import numpy as np
from solidago.poll import *
from solidago.recommenders.weights.set_weights import SetWeights


class Pivot:
    def __init__(self,
        set_weights: SetWeights | tuple[str, dict],
        shuffle: bool = True,
    ):
        import solidago, solidago.recommenders.weights as weights_module
        self.set_weights = solidago.load(set_weights, weights_module)
        self.shuffle = shuffle

    def sample_game(self, entities: Entities) -> tuple[Entity, Entity]:
        raise NotImplemented

    def pivot(self, entities: Entities, limit: int) -> Entities:
        while len(entities) > limit:
            e, f = self.sample_game(entities)
            total_weight = e["weight"] + f["weight"]
            e_win_probability = e["weight"] / total_weight
            win, loss = (e, f) if np.random.random() <= e_win_probability else (f, e)
            entities[win.name, "weight"] = total_weight
            entities = entities.drop(loss.name)
        return entities

    def __call__(self, poll: Poll, username: str, limit: int, cursor: str | None = None) -> Entities:
        entities = self.set_weights(poll, username, cursor)
        return self.pivot(entities, limit).shuffle(self.shuffle)
    