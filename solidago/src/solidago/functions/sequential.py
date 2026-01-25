import logging, numpy as np

logger = logging.getLogger(__name__)

from solidago.primitives.timer import time
from solidago.poll import *
from .poll_function import PollFunction


class Sequential(PollFunction):
    def __init__(self, modules: list | None = None, name: str | None = None, max_workers: int | None = None, seed: int | None = None):
        super().__init__(max_workers)
        self.name = name or "Sequential"
        self.seed = seed
        from solidago import load
        self.modules: list[PollFunction] = [load(m, max_workers=max_workers) for m in modules or list()]
    
    def poll2poll_function(self, poll: Poll, save_directory: str | None = None) -> Poll:
        return self(poll, save_directory)

    def __call__(self, poll: Poll, save_directory: str | None = None, skip_steps: set={}) -> Poll:
        if self.seed is not None:
            assert isinstance(self.seed, int)
            logger.info(f"Set random seed = {self.seed}")
            np.random.seed(self.seed)
            
        result = poll
        for step, module in enumerate(self.modules):
            if step in skip_steps:
                continue
            log = f"{self.name} {step+1}. {type(module).__name__}"
            with time(logger, log):
                result = module.poll2poll_function(result, save_directory)
        return result
    
    def save_result(self, poll: Poll, directory: str | None = None) -> None:
        return poll.save_instructions(directory)
    
    def args_save(self):
        return [ module.save() for module in self.modules ]
        