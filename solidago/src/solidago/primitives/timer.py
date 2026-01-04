from contextlib import contextmanager

import timeit
import logging


@contextmanager
def time(logger: logging.Logger, log: str, log_start: bool = False):
    start = timeit.default_timer()
    if log_start:
        logger.info(log)
    try:
        yield None
    finally:
        logger.info(f"{log} in {int(timeit.default_timer() - start)} seconds")
