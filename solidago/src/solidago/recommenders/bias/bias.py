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
        values = ballot.get_column("value")
        ballot_weight = values.abs().sum()
        multipliers = ballot.get_column("entity_name").map(lambda e: self.multiplier(e, poll))
        biased_values = values * multipliers
        normalized_biased_values = biased_values * ballot_weight / biased_values.abs().sum()
        ballot.set_columns(value=list(normalized_biased_values))
        return ballot