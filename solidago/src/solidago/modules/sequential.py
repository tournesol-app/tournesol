from typing import Union, Optional, Any
from pathlib import Path
from pandas import Series

import yaml
import logging

logger = logging.getLogger(__name__)

from solidago.primitives.timer import time
from solidago.poll import *
from .base import PollFunction


class Sequential(PollFunction):
    def __init__(self, modules: list, name: Optional[str]=None, max_workers: Optional[int]=None):
        super().__init__(max_workers)
        self.name = "Sequential" if name is None else name
        self.modules: list[PollFunction] = list()
        for module in modules:
            if isinstance(module, PollFunction):
                self.modules.append(module)
            elif isinstance(module, (list, tuple)) and len(module) == 2:
                import solidago.modules
                module = getattr(solidago.modules, module[0])(max_workers=max_workers, **module[1])
                assert isinstance(module, PollFunction)
                self.modules.append(module)
            else:
                print(f"Sequential.__init__: Module {module} has invalid type")
    
    def poll2poll_function(self, poll: Poll, save_directory: Optional[str]=None) -> Poll:
        return self(poll, save_directory)

    def __call__(self, poll: Poll, save_directory: Optional[str]=None, skip_steps: set={}) -> Poll:
        result = poll
        for step, module in enumerate(self.modules):
            if step in skip_steps:
                continue
            log = f"{self.name} {step+1}. {type(module).__name__}"
            with time(logger, log):
                result = module.poll2poll_function(result, save_directory)
        return result
    
    def save_result(self, poll: Poll, directory: Optional[str]=None) -> None:
        return poll.save_instructions(directory)
    
    def args_save(self):
        return [ module.save() for module in self.modules ]

    @classmethod
    def load(cls, d: Union[dict, str], max_workers: Optional[int]=None) -> "Sequential":
        if isinstance(d, str):
            with open(d) as f:
                d = yaml.safe_load(f)
        return cls(d["modules"], **{k: v for k, v in d.items() if k != "modules"})
        
    def yaml_keys(self) -> list:
        return [type(module).__name__ for module in self.modules]
