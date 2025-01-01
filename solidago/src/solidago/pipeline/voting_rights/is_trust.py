from solidago.state import *
from .base import VotingRightsAssignment


class IsTrust(VotingRightsAssignment):
    def __init__(self, privacy_penalty: float=0.5):
        """ Computes voting_rights simply as the user trust scores,
        potentially multiplied by the privacy penalty if the vote is private.
        
        Parameters
        ----------
        privacy_penalty: float
            Penalty on private entity evaluation
        """
        self.privacy_penalty = privacy_penalty
    
    def __call__(self, state: State) -> None:
        """ Compute voting rights as trust_scores """
        state.voting_rights = VotingRights()
        
        for user in state.users:
            for criterion in state.criteria:
                for entity in state.user_models[user].scored_entities(state.entities, criterion):
                    state.voting_rights[user, entity, criterion] = state.users.loc[user, "trust_score"]
                    if state.privacy[user, entity] is None:
                        state.privacy[user, entity] = False
                        state.voting_rights[user, entity, criterion] *= self.privacy_penalty
    
    def args_save(self) -> dict[str, float]:
        return { "privacy_penalty": self.privacy_penalty }
    
