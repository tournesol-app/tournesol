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
    def __init__(self):
        super().__init__()
    
    @property
    def modules(self):
        return { key: value for key, value in self.__dict__.items() if isinstance(value, StateFunction) }
    
    def __call__(self, state: State, save_directory: Optional[str]=None) -> State:
        return self.main(state, save_directory)

    def main(self, state: State, save_directory: Optional[str]=None) -> State:
        result = state.copy()
        type2keys = { value: key for key, value in self.state_cls.__init__.__annotations__.items() }
        start = timeit.default_timer()
        for step, (key, module) in enumerate(self.modules.items()):
            logger.info(f"Step {step}. Doing {key} with {type(module).__name__}")
            value = module(state)
            stop = timeit.default_timer()
            logger.info(f"Step {step}. Terminated in {round(stop - start, 2)} seconds")
            start = stop
            module.assign(result, value)
            module.save_result(result, save_directory)
        return result
    
    def args_save(self):
        return [ module.save() for module in self.modules ]
