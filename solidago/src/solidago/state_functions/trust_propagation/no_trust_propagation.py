from dataclasses import dataclass

from solidago.state import State
from solidago.state_functions.base import StateFunction


class NoTrustPropagation(StateFunction):
    def __init__(self, pretrust_value: float=0.8, *args, **kwargs):
        """
        Parameters
        ----------
        pretrust_value:
            trust score to assign to pretrusted users
        """
        super().__init__(*args, **kwargs)
        self.pretrust_value = pretrust_value

    def __call__(self, state: State) -> State:
        users = state.users
        return state.assign(
            users=users.assign(
                trust=users.values("is_pretrusted") * self.pretrust_value
            )
        )
