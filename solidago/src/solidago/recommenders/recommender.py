from solidago.poll import *


class Recommender:
    def __call__(self, 
        poll: Poll, 
        limit: int, 
        receiver_name: str | None = None, 
        cursor: str | None = None,
        time: int | None = None,
    ) -> Entities:
        """
        Parameters
        ----------
        limit: int
            Maximal number of entities returned
        cursor: str | None
            Typically the offset for pagination
        time: int | float | None 
            Unix time in seconds. Set to datetime.now() if time is None.

        See https://github.com/MarshalX/bluesky-feed-generator/blob/main/server/app.py 
        for a simple atproto implementation """
        raise NotImplemented
    