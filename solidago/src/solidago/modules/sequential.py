from typing import Union, Optional, Any
from pathlib import Path
from pandas import Series

import json
import logging

logger = logging.getLogger(__name__)

from solidago.primitives.timer import time
from solidago.state import *
from .base import StateFunction


class Sequential(StateFunction):
    def __init__(self, name: Optional[str]=None, max_workers: Optional[int]=None, **kwargs):
        super().__init__(max_workers)
        self.name = "Sequential" if name is None else name
        for key, value in kwargs.items():
            if isinstance(value, StateFunction):
                setattr(self, key, value)
            elif isinstance(value, (list, tuple)) and len(value) == 2:
                import solidago.modules as modules
                setattr(self, key, getattr(modules, value[0])(**value[1]))
            else:
                value_type = type(value).__name__
                print(f"Sequential.__init__: Unhandled input key={key}, type(value)={value_type}")
    
    @property
    def modules(self):
        return {k: v for k, v in self.__dict__.items() if isinstance(v, StateFunction) }
    
    def state2state_function(self, state: State, save_directory: Optional[str]=None) -> State:
        return self(state, save_directory)

    def __call__(self, state: State, save_directory: Optional[str]=None, skip_steps: set={}) -> State:
        result = state
        for step, (key, module) in enumerate(self.modules.items()):
            if step in skip_steps or key in skip_steps:
                continue
            log = f"{self.name} {step+1}. {key} with {type(module).__name__}"
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
        import solidago.modules
        return cls(**{ 
            key: getattr(solidago.modules, value[0])(max_workers=max_workers, **value[1]) 
            for key, value in d.items() if key not in cls.__init__.__annotations__
        }, **{ key: value for key, value in d.items() if key in cls.__init__.__annotations__ })
        
    def json_keys(self) -> list:
        return [key for key in self.__dict__ if key[0] != "_" and hasattr(self, key)]
