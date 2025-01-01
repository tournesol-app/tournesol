from typing import Union, Optional
from pathlib import Path

from solidago.state import *
from .base import StateFunction


class Identity(StateFunction):
    def main(self, state: State) -> State:
        return state.copy()
