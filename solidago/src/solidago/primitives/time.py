from contextlib import contextmanager
from datetime import datetime, timedelta
from timeit import default_timer
from typing import Self, overload

import numpy as np
import logging


DateInput = datetime | dict | str | int | np.integer | float
DurationInput = timedelta | dict | int | np.integer | float

class Date:
    def __init__(self, date: DateInput): 
        if isinstance(date, (int, np.integer, float)):
            self.date = datetime.fromtimestamp(float(date))
        elif isinstance(date, str):
            self.date = datetime.fromisoformat(date)
        elif isinstance(date, dict):
            self.date = datetime(**date)
        else:
            self.date = date

    def timestamp(self) -> float:
        return self.date.timestamp()
    
    def __add__(self, other: "Duration") -> Self:
        return type(self)(self.date + other.duration)
    
    @overload
    def __sub__(self, other: "Duration") -> Self: ...
    @overload
    def __sub__(self, other: Self) -> "Duration": ...
    def __sub__(self, other):
        if isinstance(other, Date):
            return Duration(self.date - other.date)
        assert isinstance(other, Duration)
        return Date(self.date - other.duration)

    @classmethod
    def now(cls) -> Self:
        return cls(datetime.now())
    
    def __bool__(self) -> bool:
        return True
    
    def __repr__(self) -> str:
        return repr(self.date)


class Duration:
    def __init__(self, 
        duration: DurationInput | None = None, 
        default: DurationInput | None = None, 
        **kwargs
    ):
        d = default if duration is None else duration
        d = kwargs if d is None else d
        assert isinstance(d, DurationInput)
        self.duration = Duration._load(d)

    @staticmethod
    def _load(duration: DurationInput) -> timedelta:
        if isinstance(duration, (int, np.integer, float)):
            return timedelta(seconds=float(duration))
        if isinstance(duration, dict):
            return timedelta(**duration)
        return duration

    @property
    def total_seconds(self) -> float:
        return self.duration.total_seconds()
    
    def __bool__(self) -> bool:
        return True
    
    def __repr__(self) -> str:
        return repr(self.duration)


@contextmanager
def timeit(
    log: str, 
    logger: logging.Logger | type | None = None, 
    log_start: bool = False, 
    unit: str="seconds"
):
    start = default_timer()
    logger = logging if logger is None else logger
    if log_start:
        logger.info(log)
    try:
        yield None
    finally:
        if unit == "seconds":
            logger.info(f"{log} in {int(default_timer() - start)} seconds")
        elif unit == "ms":
            logger.info(f"{log} in {int(1000*(default_timer() - start))} ms")

