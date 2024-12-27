from typing import Union, Optional
from pathlib import Path

import json

from solidago.state import State
from .base import StateFunction


class Sequential(StateFunction):
    def __init__(self, *modules):
        for module in modules:
            assert isinstance(module, StateFunction)
        self.modules = modules
    
    def __call__(self, state: State) -> None:
        for module in self.modules:
            module(state)

    def args_save(self):
        return [ module.save() for module in self.modules ]
