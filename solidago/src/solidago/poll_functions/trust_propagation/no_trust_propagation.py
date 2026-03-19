from dataclasses import dataclass

from solidago.poll import Poll
from solidago.poll_functions.base import PollFunction


class NoTrustPropagation(PollFunction):
    def __init__(self, pretrust_value: float=0.8, *args, **kwargs):
        """
        Parameters
        ----------
        pretrust_value:
            trust score to assign to pretrusted users
        """
        super().__init__(*args, **kwargs)
        self.pretrust_value = pretrust_value

    def __call__(self, state: Poll) -> Poll:
        users = state.users
        return state.assign(
            users=users.assign(
                trust=users.values("is_pretrusted") * self.pretrust_value
            )
        )
