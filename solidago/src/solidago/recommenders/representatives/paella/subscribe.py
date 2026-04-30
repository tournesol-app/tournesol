from solidago.poll import *
from .weights_compute import WeightsCompute


class Subscribe(WeightsCompute):
    def __call__(self, 
        poll: Poll, 
        username: str, 
        column_name: str = "weight", 
        cursor: str | None = None
    ) -> Entities:
        subscriptions = poll.socials.filters(by=username, kind="follow").keys("to")
        df = poll.entities.df
        df = df[df["author"].isin(subscriptions)]
        df[column_name] = 1
        return Entities(df)

