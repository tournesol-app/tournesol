from numpy.typing import NDArray
import numpy as np

from solidago.poll import *
from solidago.functions.poll_function import PollFunction


class Normalize(PollFunction):
    def __init__(self, 
        qs: dict[str, float] | None = None, 
        default_q: float = float("inf")
    ):
        super().__init__(max_workers=1)
        assert default_q >= 1
        self.default_q = default_q
        self.qs = qs or dict()

    @staticmethod
    def norm(x: NDArray[np.float64], q: float) -> float:
        if np.isinf(q):
            return np.abs(x).max()
        return np.power(np.power(np.abs(x), q).sum(), 1./q)

    def multiplier(self, x: NDArray[np.float64], q: float) -> Score:
        norm = Normalize.norm(x, q)
        return Score(1. / norm) if norm > 0 else Score(1)

    def fn(self, entities: Entities, user_models: UserModels) -> UserModels:
        scores = user_models(entities)
        multipliers = UserMultipliers(keynames=["username", "criterion"])
        for (username, criterion), subscores in scores.iter("username", "criterion"):
            q = self.qs[str(criterion)] if criterion in self.qs else self.default_q
            multiplier = self.multiplier(subscores("value"), q)
            multipliers.append(multiplier, username=username, criterion=criterion)
        return user_models.user_scale(multipliers, note=type(self).__name__)
    

class MaxNorm(Normalize):
    def __init__(self, 
        qs: dict[str, float] | None = None, 
        default_q: float = float("inf"), 
        max: float = 1.
    ):
        super().__init__(qs, default_q)
        assert max > 0
        self.max = max
    
    def multiplier(self, x: NDArray[np.float64], q: float) -> Score:
        return Score(1. / max(self.max, Normalize.norm(x, q)))