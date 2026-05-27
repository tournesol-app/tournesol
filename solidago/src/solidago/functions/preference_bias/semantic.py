from numpy.typing import NDArray

import numpy as np

from solidago.poll import *
from .bias import PreferenceBias


class SemanticBias(PreferenceBias):
    def __init__(self, 
        username: str | None = None, 
        bias: float = 1., 
        *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.username = username
        self.bias = bias

    def _multipliers(self,  # type: ignore
        scores: Scores, 
        users: Users,
        entities: Entities,
    ) -> tuple[NDArray, NDArray | float, NDArray | float]:
        assert self.username is not None, f"Ran {type(self).__name__} with receiver"
        entities = entities.filters(scores("entity_names"))
        vector = users[self.username].vector
        unit = vector / np.sqrt((vector**2).sum())
        unit_embeddings = entities.vectors / np.sqrt((entities.vectors**2).sum(axis=0))
        return np.power(1 + unit @ unit_embeddings, self.bias), 0., 0.