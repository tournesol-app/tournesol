from numpy.typing import NDArray
from numba import njit

import numpy as np, pandas as pd

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




def add(df: pd.DataFrame, column: str, value: float) -> NDArray[np.float64]:
    x: list[float] = list()
    for _, row in df.iterrows():
        x.append(row[column] + value)
    return np.array(x)

def add2(df: pd.DataFrame, column: str, value: float) -> NDArray[np.float64]:
    return (df[column] + value).astype(np.float64).to_numpy()


if __name__ == "__main__":
    df = pd.DataFrame({"float": np.arange(1_000_000)})
    with time("Nonjitted add"):
        print(add(df, "float", 10))
    with time("Pandas add"):
        print(add2(df, "float", 10))


