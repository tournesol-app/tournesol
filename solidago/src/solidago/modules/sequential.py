from typing import Union, Optional, Any
from pathlib import Path
from pandas import Series

import json
import logging

logger = logging.getLogger(__name__)

from solidago.primitives.timer import time
from solidago.poll import *
from .base import StateFunction


class Sequential(StateFunction):
    def __init__(self, modules: list, name: Optional[str]=None, max_workers: Optional[int]=None):
        super().__init__(max_workers)
        self.name = "Sequential" if name is None else name
        self.modules = list()
        for module in modules:
            if isinstance(module, StateFunction):
                self.modules.append(module)
            elif isinstance(module, (list, tuple)) and len(module) == 2:
                import solidago.modules
                self.modules.append(
                    getattr(solidago.modules, module[0])(max_workers=max_workers, **module[1])
                )
            else:
                print(f"Sequential.__init__: Module {module} has invalid type")
    
    def state2state_function(self, state: State, save_directory: Optional[str]=None) -> State:
        return self(state, save_directory)

    def __call__(self, state: State, save_directory: Optional[str]=None, skip_steps: set={}) -> State:
        result = state
        for step, module in enumerate(self.modules):
            if step in skip_steps:
                continue
            log = f"{self.name} {step+1}. {type(module).__name__}"
            with time(logger, log):
                result = module.state2state_function(result, save_directory)
        return result
    
    def save_result(self, state: State, directory: Optional[str]=None) -> None:
        return state.save_instructions(directory)
    
    def args_save(self):
        return [ module.save() for module in self.modules ]

    @classmethod
    def load(cls, d: Union[dict, str], max_workers: Optional[int]=None) -> "Sequential":
        if isinstance(d, str):
            with open(d) as f:
                d = json.load(f)
        return cls(d["modules"], **{k: v for k, v in d.items() if k != "modules"})
        
    def json_keys(self) -> list:
        return [type(module).__name__ for module in self.modules]
