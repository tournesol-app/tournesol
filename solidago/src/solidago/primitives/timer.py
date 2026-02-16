from contextlib import contextmanager

import timeit
import logging


@contextmanager
def time(log: str, logger: logging.Logger | type | None = None, log_start: bool = False, unit: str="seconds"):
    start = timeit.default_timer()
    logger = logging if logger is None else logger
    if log_start:
        logger.info(log)
    try:
        yield None
    finally:
        if unit == "seconds":
            logger.info(f"{log} in {int(timeit.default_timer() - start)} seconds")
        elif unit == "ms":
            logger.info(f"{log} in {int(1000*(timeit.default_timer() - start))} ms")

