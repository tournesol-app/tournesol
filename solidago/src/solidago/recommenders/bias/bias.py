from abc import abstractmethod
import numpy as np
from solidago.poll import *

class BallotBiasing:
    @abstractmethod
    def __call__(self, poll: Poll, ballot: Scores) -> Scores:
        raise NotImplemented


class WeightPreservingBias:
    @abstractmethod
    def multiplier(self, entity_name: str, poll: Poll) -> np.float64:
        raise NotImplemented

    def __call__(self, poll: Poll, ballot: Scores) -> Scores:
        values = ballot("value")
        ballot_weight = np.abs(values).sum()
        multipliers = np.array(list(map(lambda e: self.multiplier(e, poll), ballot("entity_name"))))
        biased_values = values * multipliers
        normalized_biased_values = biased_values * ballot_weight / np.abs(biased_values).sum()
        ballot.set_columns(value=list(normalized_biased_values))
        return ballot