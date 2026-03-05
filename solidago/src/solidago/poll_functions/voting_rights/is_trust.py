from solidago.poll import *
from solidago.poll_functions.poll_function import PollFunction


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
    
    def fn(self, 
        users: Users, 
        entities: Entities, 
        public_settings: PublicSettings,
        ratings: Ratings, 
        comparisons: Comparisons
    ) -> VotingRights:
        """ Compute voting rights as trust_scores """
        voting_rights = VotingRights()

        for user in users:
            for entity in entities:
                for criterion in ratings.keys("criterion") | comparisons.keys("criterion"):
                    penalty = public_settings.penalty(self.privacy_penalty, username=user.name, entity_name=entity.name)
                    voting_rights.set(
                        username=user.name, 
                        entity_name=entity.name, 
                        criterion=criterion, 
                        voting_right=penalty * user["trust"]
                    )
        
        return voting_rights
