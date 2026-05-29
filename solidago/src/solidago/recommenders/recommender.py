from contextlib import contextmanager
import timeit

from solidago.poll import *
from solidago.primitives.time import DateInput

import logging
logger = logging.getLogger("solidago.recommenders")


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
    
    @contextmanager
    def timeit(self, log: str, log_start: bool = False, unit: str="seconds"):
        start = timeit.default_timer()
        if log_start:
            logger.info(log)
        try:
            yield None
        finally:
            if unit == "seconds":
                logger.info(f"{log} in {int(timeit.default_timer() - start)} seconds")
            elif unit == "ms":
                logger.info(f"{log} in {int(1000*(timeit.default_timer() - start))} ms")
