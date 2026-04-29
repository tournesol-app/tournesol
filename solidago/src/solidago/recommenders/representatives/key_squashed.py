from numpy.typing import NDArray
import numpy as np
from datetime import datetime

from solidago.poll import *
from .weights_compute import WeightsCompute
from .subscribe import Subscribe


def squash(x: NDArray) -> NDArray:
    """ Must map [0, inf] to [0, 1] increasingly and bijectively """
    return np.where(x == np.inf, 1., x / (1. + x))

def shifted_squash(x: NDArray, max: float) -> NDArray:
    """ Must map [0, inf] to [1, max] increasingly and bijectively """
    return (max - 1.) * squash(x) + 1.


class KeySquashed(WeightsCompute):
    def __init__(self, 
        ratio_time: float, 
        ratio_utility: float, 
        ratio_key: float,
        default_decay_time: float,
        key: str = "author",
        utility_compute: WeightsCompute | None = None,
    ):
        assert ratio_time >= 1, ratio_time
        self.ratio_time = ratio_time
        assert ratio_utility >= 1, ratio_utility
        self.ratio_utility = ratio_utility
        assert ratio_key >= 1, ratio_key
        self.ratio_key = ratio_key
        assert default_decay_time > 0, default_decay_time
        self.default_decay_time = default_decay_time
        self.key = key
        self.utility_compute = Subscribe() if utility_compute is None else utility_compute

    def __call__(self, 
        poll: Poll, 
        username: str, 
        column_name: str = "weight", 
        cursor: str | None = None
    ) -> Entities:
        entities = self.utility_compute(poll, username, "utility", cursor)
        user = poll.users[username]
        assert isinstance(user, User)
        # Compute time utility
        t = user["update_time"] if "update_time" in user else self.default_decay_time
        age = datetime.now().second - entities.get_column("creation_date").to_numpy(np.float64)
        time_utilities = shifted_squash(t / age, self.ratio_time)
        # Combine with timeless utility
        timeless_utilities = poll.entities.get_column("timeless_utility").to_numpy(np.float64)
        entities.set_column("utility", time_utilities * shifted_squash(timeless_utilities, self.ratio_utility))
        for _, indices in entities.df.groupby(self.key).indices.items():
            group = entities.filters(indices)
            assert isinstance(group, Entities), group
            group_utility_sum = group.get_column("utility").sum()
            for index in indices:
                e = entities.index2name(index)
                entities[e, column_name] = group[e]["utility"] / group_utility_sum
        return entities