from typing import Union, Optional
from pathlib import Path

from solidago.state import *
from .base import StateFunction


class Identity(StateFunction):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def __call__(self, state: State) -> State:
        return state.copy()
