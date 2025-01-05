from typing import Union, Optional, Any
from pathlib import Path
from pandas import Series

import json
import timeit
import logging

logger = logging.getLogger(__name__)

from solidago.state import State
from .base import StateFunction


class Sequential(StateFunction):
    def __init__(self, **kwargs):
        super().__init__()
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    @property
    def modules(self):
        return { key: value for key, value in self.__dict__.items() if isinstance(value, StateFunction) }
    
    def state_function(self, state: State, save_directory: Optional[str]=None) -> State:
        return self(state, save_directory)

    def __call__(self, state: State, save_directory: Optional[str]=None) -> State:
        result = state.copy()
        start = timeit.default_timer()
        for step, (key, module) in enumerate(self.modules.items()):
            logger.info(f"Step {step}. Doing {key} with {type(module).__name__}")
            value = module.state_function(result)
            stop = timeit.default_timer()
            logger.info(f"Step {step}. Terminated in {round(stop - start, 2)} seconds")
            start = stop
            module.assign(result, value)
            module.save_result(result, save_directory)
        return result
    
    def args_save(self):
        return [ module.save() for module in self.modules ]

    @classmethod
    def load(cls, d: Union[dict, str]) -> "Sequential":
        if isinstance(d, str):
            with open(d) as f:
                d = json.load(d)
        import solidago.pipeline as pipeline
        return cls(**{ key: getattr(pipeline, d[key][0])(**d[key][1]) for key in d })
