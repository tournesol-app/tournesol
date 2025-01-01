from solidago.state import *
from solidago.pipeline.base import StateFunction


class VotingRightsAssignment(StateFunction):
    def main(self, voting_rights: VotingRights) -> VotingRights:
        return state.voting_rights
