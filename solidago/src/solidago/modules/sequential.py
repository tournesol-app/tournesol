from typing import Union, Optional, Any
from pathlib import Path
from pandas import Series

import json
import timeit
import logging

logger = logging.getLogger(__name__)

from solidago.state import *
from .base import StateFunction


class Sequential(StateFunction):
    def __init__(self, name: Optional[str]=None, **kwargs):
        super().__init__()
        self.name = "Sequential" if name is None else name
        for key, value in kwargs.items():
            if isinstance(value, StateFunction):
                setattr(self, key, value)
            elif isinstance(value, (list, tuple)) and len(value) == 2:
                import solidago.modules as modules
                setattr(self, key, getattr(modules, value[0])(**value[1]))
            else:
                print(f"Sequential.__init__: Got unhandled input key={key}, type(value)={type(value).__name__}")
    
    @property
    def modules(self):
        return { key: value for key, value in self.__dict__.items() if isinstance(value, StateFunction) }
    
    def state_function(self, state: State, save_directory: Optional[str]=None) -> State:
        return self(state, save_directory)

    def __call__(self, state: State, save_directory: Optional[str]=None, skip_steps: set[int]={}) -> State:
        result = state
        for step, (key, module) in enumerate(self.modules.items()):
            if step in skip_steps:
                continue
            start = timeit.default_timer()
            logger.info(f"Step {step + 1} of {self.name}. Doing {key} with {type(module).__name__}")
            result = module.state2state_function(result, save_directory)
            stop = timeit.default_timer()
            logger.info(f"Step {step + 1} of {self.name}. Terminated in {round(stop - start, 2)} seconds")
        return result
    
    def args_save(self):
        return [ module.save() for module in self.modules ]

    @classmethod
    def load(cls, d: Union[dict, str], submodule=None) -> "Sequential":
        if isinstance(d, str):
            with open(d) as f:
                d = json.load(f)
        return cls(**{ 
            key: cls.load_module(key if submodule is None else submodule, value[0], value[1]) 
            for key, value in d.items() if key not in Sequential.__init__.__annotations__
        }, **{ key: value 
            for key, value in d.items() if key in Sequential.__init__.__annotations__ 
        })
        
    @classmethod
    def load_module(cls, key: str, cls_name: str, kwargs: dict) -> StateFunction:
        if cls_name == "Sequential":
            return cls.load(kwargs, key)
        import solidago.modules
        if cls_name == "Identity":
            return solidago.modules.Identity()
        return getattr(getattr(solidago.modules, key), cls_name)(**kwargs)

    def json_keys(self) -> list:
        return list(
            key for key in self.__dict__
            if key[0] != "_" and hasattr(self, key)
        )
