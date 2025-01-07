from solidago._state import *
from solidago._pipeline.base import StateFunction


class IsTrust(StateFunction):
    def __init__(self, privacy_penalty: float=0.5):
        """ Computes voting_rights simply as the user trust scores,
        potentially multiplied by the privacy penalty if the vote is private.
        
        Parameters
        ----------
        privacy_penalty: float
            Penalty on private entity evaluation
        """
        self.privacy_penalty = privacy_penalty
    
    def __call__(self, 
        users: Users, 
        entities: Entities, 
        made_public: MadePublic,
        assessments: Assessments, 
        comparisons: Comparisons
    ) -> VotingRights:
        """ Compute voting rights as trust_scores """
        voting_rights = VotingRights()
        criteria = assessments.get_set("criterion") | comparisons.get_set("criterion")
        
        for user in users:
            for entity in entities:
                for criterion in criteria:
                    voting_right = users.loc[user, "trust_score"]
                    if not made_public[user, entity]:
                        voting_right *= self.privacy_penalty
                    voting_rights.add_row((user, entity), { criterion: voting_right })
        
        return voting_rights
