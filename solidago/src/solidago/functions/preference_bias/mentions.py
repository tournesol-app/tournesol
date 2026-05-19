from numpy.typing import NDArray

import numpy as np

from solidago.poll import *
from .bias import PreferenceBias


class MentionBias(PreferenceBias):
    def __init__(self, receiver: User | None = None, multiplier: float = 5., *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.receiver = receiver
        self.multiplier = multiplier

    def _multipliers(self,  # type: ignore
        scores: Scores, 
        entities: Entities
    ) -> tuple[NDArray, NDArray | float, NDArray | float]:
        assert self.receiver is not None, f"Ran {type(self).__name__} without receiver"
        entities = entities.filters(scores("entity_names"))
        mentions = np.array(self.receiver.name in m for m in entities("mentions", ()))
        return 1 + mentions * self.multiplier, 0., 0.