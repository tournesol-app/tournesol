from solidago.poll import *
from .base import PollFunction


class Identity(PollFunction):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def __call__(self, poll: Poll) -> Poll:
        return poll.copy()
