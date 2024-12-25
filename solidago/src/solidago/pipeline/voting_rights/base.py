from solidago.state import *
from solidago.pipeline.base import StateFunction


class VotingRightsAssignment(StateFunction):
    def __init__(self):
        super().__init__()
