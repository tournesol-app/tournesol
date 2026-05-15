from numpy.typing import NDArray

import numpy as np

from solidago.poll import *
from .bias import PreferenceBias


class SemanticBias(PreferenceBias):
    def __init__(self, 
        receiver: User | None = None, 
        bias: float = 1., 
        *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.receiver = receiver
        self.bias = bias

    def _multipliers(self,  # type: ignore
        scores: Scores, 
        entities: Entities
    ) -> tuple[NDArray, NDArray | float, NDArray | float]:
        assert self.receiver is not None, f"Ran {type(self).__name__} with receiver"
        entities = entities.filters(scores("entity_names"))
        unit = self.receiver.vector / np.sqrt((self.receiver.vector**2).sum())
        unit_embeddings = entities.vectors / np.sqrt((entities.vectors**2).sum(axis=0))
        return np.power(1 + unit @ unit_embeddings, self.bias), 0., 0.