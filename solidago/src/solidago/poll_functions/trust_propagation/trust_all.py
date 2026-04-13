from solidago.poll import Poll
from solidago.poll_functions.base import PollFunction


class TrustAll(PollFunction):
    """`TrustAll` is a naive solution that assignes an equal amount of trust to all users"""
    def __call__(self, state: Poll) -> Poll:
        return state.assign(
            users=state.users.assign(trust=1.0)
        )
