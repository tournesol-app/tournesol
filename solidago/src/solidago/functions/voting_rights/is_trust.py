from solidago.poll import *
from solidago.functions.base import PollFunction


class Trust2VotingRights(PollFunction):
    def __init__(self, privacy_penalty: float=0.5, *args, **kwargs):
        """ Computes voting_rights simply as the user trust scores,
        potentially multiplied by the privacy penalty if the vote is private.
        
        Parameters
        ----------
        privacy_penalty: float
            Penalty on private entity evaluation
        """
        super().__init__(*args, **kwargs)
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
        
        for user in users:
            for entity in entities:
                for criterion in assessments.keys("criterion") | comparisons.keys("criterion"):
                    penalty = made_public.penalty(self.privacy_penalty, user, entity)
                    voting_rights[user, entity, criterion] = penalty * user.trust
        
        return voting_rights
