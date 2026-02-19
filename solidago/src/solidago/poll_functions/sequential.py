import logging, numpy as np
from typing import Any

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
            import solidago
            subfunction = solidago.load(sub, solidago.poll_functions, max_workers=max_workers) 
            assert isinstance(subfunction, PollFunction)
            self.subfunctions.append(subfunction)
            
    def poll2poll_function(self, poll: Poll, save_directory: str | None = None) -> Poll:
        return self(poll, save_directory)

    def __getitem__(self, index: int) -> PollFunction:
        return self.subfunctions[index]

    def __call__(self, poll: Poll | None = None, save_directory: str | None = None, skip_steps: set[int] | None = None) -> Poll:
        if self.seed is not None:
            assert isinstance(self.seed, int)
            logger.info(f"Set random seed = {self.seed}")
            np.random.seed(self.seed)
        result = poll or Poll()
        for step, subfunction in enumerate(self.subfunctions):
            if skip_steps is not None and step in skip_steps:
                continue
            log = f"{self.name} {step+1}. {type(subfunction).__name__}"
            with time(log, logger):
                result = subfunction.poll2poll_function(result, save_directory)
        return result
    
    def save_result(self, poll: Poll, directory: str | None = None) -> tuple[str, dict[str, Any]] | None:
        return poll.save_instructions(directory)
    
    def args_save(self):
        return [ subfunction.save() for subfunction in self.subfunctions ]
        