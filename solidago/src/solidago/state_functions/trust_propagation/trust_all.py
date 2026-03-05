from solidago.state import State
from solidago.state_functions.base import StateFunction


class TrustAll(StateFunction):
    """`TrustAll` is a naive solution that assignes an equal amount of trust to all users"""
    def __call__(self, state: State) -> State:
        return state.assign(
            users=state.users.assign(trust=1.0)
        )
