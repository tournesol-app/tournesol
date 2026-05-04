from numpy.typing import NDArray
import numpy as np

from solidago.poll import *
from solidago.poll_functions.poll_function import PollFunction


class Normalize(PollFunction):
    default_qs: dict[str, float] = dict(post=1., repost=2., report=2.)

    def __init__(self, q: float = float("inf"), qs: dict[str, float] | None = None):
        assert q >= 1
        self.q = q
        self.qs = qs or self.default_qs

    def norm(self, x: NDArray[np.float64], q: float) -> float:
        return x.max() if np.isinf(q) else np.power(np.power(np.abs(x), q).sum(), 1./q)

    def multiplier(self, x: NDArray[np.float64], q: float) -> Score:
        norm = self.norm(x, q)
        return Score(1. / norm) if norm > 0 else Score(1)

    def fn(self, entities: Entities, user_models: UserModels) -> UserModels:
        scores = user_models(entities)
        multipliers = UserMultipliers(keynames=["username", "criterion"])
        for (username, criterion), subscores in scores.iter("username", "criterion"):
            assert isinstance(subscores, Scores)
            q = self.qs[str(criterion)] if criterion in self.qs else self.q
            multiplier = self.multiplier(subscores("value"), q)
            multipliers.append(multiplier, username=username, criterion=criterion)
        return user_models.user_scale(multipliers, note=type(self).__name__)
    

class MaxNorm(Normalize):
    def __init__(self, q: float = float("inf"), qs: dict[str, float] | None = None, max: float = 1.):
        super().__init__(q)
        assert max >= 0
        self.max = max
    
    def multiplier(self, x: NDArray[np.float64], q: float) -> Score:
        return Score(1. / max(self.max, self.norm(x, q)))