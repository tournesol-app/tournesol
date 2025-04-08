from contextlib import contextmanager

import timeit
import logging


@contextmanager
def time(logger: logging.Logger, log: str):
    start = timeit.default_timer()
    logger.info(log)
    try:
        yield None
    finally:
        logger.info(f"{log} in {int(timeit.default_timer() - start)} seconds")
