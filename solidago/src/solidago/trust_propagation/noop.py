import pandas as pd

from .base import TrustPropagation


class NoopTrust(TrustPropagation):
    """
    Noop for trust propagation:
    trust scores are simply read from the input dataframe
    """

    def __call__(self, users: pd.DataFrame, _vouches: pd.DataFrame) -> pd.DataFrame:
        return pd.DataFrame(
            {
                "is_pretrusted": users["is_pretrusted"],
                "trust_score": users["trust_score"].fillna(0.0),
            },
            index=users.index,
        )

    def __str__(self):
        return type(self).__name__

    def to_json(self):
        return (type(self).__name__,)
