from numpy.typing import NDArray
import numpy as np

from solidago.poll import *
from solidago.functions.poll_function import PollFunction


class Normalize(PollFunction):
    def __init__(self, 
        qs: dict[str, float] | None = None, 
        default_q: float = float("inf"),
        to_direct: bool = False,
    ):
        super().__init__(max_workers=1)
        assert default_q >= 1
        self.default_q = default_q
        self.qs = qs or dict()
        self.to_direct = to_direct

    @staticmethod
    def norm(x: NDArray[np.float64], q: float) -> float:
        if np.isinf(q):
            return np.abs(x).max()
        return np.power(np.power(np.abs(x), q).sum(), 1./q)

    def multiplier(self, x: NDArray[np.float64], q: float) -> float:
        norm = Normalize.norm(x, q)
        return 1. / norm if norm > 0 else 1.

    def fn(self, entities: Entities, user_models: UserModels) -> UserModels:
        scores = user_models(entities)
        multipliers_list = list()
        for (u, c), s in scores.iter("username", "criterion"):
            q = self.qs[str(c)] if c in self.qs else self.default_q
            multipliers_list.append((u, c, self.multiplier(s("value"), q)))
        multipliers = UserMultipliers(
            multipliers_list, 
            columns=["username", "criterion", "value"],
            keynames=["username", "criterion"],
        ).add_columns(left_unc=0, right_unc=0)
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
    
    def multiplier(self, x: NDArray[np.float64], q: float) -> float:
        return 1. / max(self.max, Normalize.norm(x, q))