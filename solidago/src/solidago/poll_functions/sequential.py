import logging, numpy as np
from typing import Any, Iterator, Self

logger = logging.getLogger(__name__)

from solidago.primitives.timer import time
from solidago.poll import *
from .poll_function import PollFunction


class Sequential(PollFunction):
    def __init__(self, 
        subfunctions: list | None = None, 
        name: str | None = None, 
        max_workers: int | None = None, 
        seed: int | None = None
    ):
        super().__init__(max_workers)
        self.name = name or "Sequential"
        self.seed = seed
        self.subfunctions: list[PollFunction] = list()
        for sub in subfunctions or list():
            import solidago, solidago.poll_functions as m
            subfunction = solidago.load(sub, m, PollFunction, max_workers=max_workers) 
            assert isinstance(subfunction, PollFunction)
            self.subfunctions.append(subfunction)
            
    def __call__(self, poll: Poll, save_directory: str | None = None) -> Poll:
        return self.fn(poll, save_directory)

    def customize(self, user: User, time: int | None = None) -> Self:
        subfunctions = [f.customize(user, time) for f in self.subfunctions]
        return type(self)(subfunctions, self.name, self.max_workers, self.seed)
    
    def __getitem__(self, index: int) -> PollFunction:
        return self.subfunctions[index]
    
    def __iter__(self) -> Iterator[PollFunction]:
        for subfunction in self.subfunctions:
            yield subfunction
    
    def __len__(self) -> int:
        return len(self.subfunctions)
    
    def fn(self, poll: Poll | None = None, save_directory: str | None = None, skip_steps: set[int] | None = None) -> Poll:
        if self.seed is not None:
            assert isinstance(self.seed, int)
            logger.info(f"Set random seed = {self.seed}")
            np.random.seed(self.seed)
        result = poll or Poll()
        for step, subfunction in enumerate(self):
            if skip_steps is not None and step in skip_steps:
                continue
            log = f"{self.name} {step+1}. {type(subfunction).__name__}"
            with time(log, logger):
                result = subfunction(result, save_directory)
        return result
    
    def save_result(self, poll: Poll, directory: str | None = None) -> tuple[str, dict[str, Any]] | None:
        return poll.save_instructions(directory)
    
    def args_save(self):
        return [ subfunction.save() for subfunction in self.subfunctions ]
        