from contextlib import contextmanager

from datetime import datetime, timedelta
from timeit import default_timer
import logging
from typing import Self, overload

DateInput = datetime | dict | str | int | float
DurationInput = timedelta | dict | int

class Date:
    def __init__(self, date: DateInput): 
        if isinstance(date, (int, float)):
            self.date = datetime.fromtimestamp(date)
        elif isinstance(date, str):
            self.date = datetime.fromisoformat(date)
        elif isinstance(date, dict):
            self.date = datetime(**date)
        else:
            self.date = date

    @property
    def seconds(self) -> int:
        return self.date.second
    
    @classmethod
    def now(cls) -> Self:
        return cls(datetime.now())
    
    def __bool__(self) -> bool:
        return True


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
        if isinstance(duration, (int, float)):
            return timedelta(seconds=duration)
        if isinstance(duration, dict):
            return timedelta(**duration)
        return duration

    @property
    def seconds(self) -> int:
        return self.duration.seconds
    
    def __bool__(self) -> bool:
        return True


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

