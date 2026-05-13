from solidago.poll import *
from solidago.primitives.time import DateInput


class Recommender:
    def __call__(self, 
        poll: Poll, 
        limit: int, 
        receiver_name: str | None = None, 
        cursor: str | None = None,
        date: DateInput | None = None,
    ) -> Entities:
        """
        Parameters
        ----------
        limit: int
            Maximal number of entities returned
        cursor: str | None
            Typically the offset for pagination
        date: datetime | dict | str | int | float | None
            Unix time in seconds. Set to datetime.now() if time is None.

        See https://github.com/MarshalX/bluesky-feed-generator/blob/main/server/app.py 
        for a simple atproto implementation """
        raise NotImplemented
    