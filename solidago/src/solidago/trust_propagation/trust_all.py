from .base import TrustPropagation

import pandas as pd


class TrustAll(TrustPropagation):
    """`TrustAll` is a naive solution that assignes an equal amount of trust to all users"""

    def __call__(self, users: pd.DataFrame, vouches: pd.DataFrame):
        return users.assign(trust_score=1.0)
