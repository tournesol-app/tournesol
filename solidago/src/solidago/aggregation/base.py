from abc import abstractmethod
from typing import Mapping

import pandas as pd

from solidago.voting_rights import VotingRights
from solidago.scoring_model import ScoringModel


class Aggregation:
    @abstractmethod
    def __call__(
        self, 
        voting_rights: VotingRights,
        user_models: Mapping[int, ScoringModel],
        users: pd.DataFrame,
        entities: pd.DataFrame
    ) -> tuple[dict[int, ScoringModel], ScoringModel]:
        """ Returns scaled user models
        
        Parameters
        ----------
        voting_rights: VotingRights
            voting_rights[user, entity]: float
        user_models: dict[int, ScoringModel]
            user_models[user] is user's scoring model
        users: DataFrame with columns
            * user_id (int, index)
            * trust_score (float)
        entities: DataFrame with columns
            * entity_id (int, ind)

        Returns
        -------
        updated_user_models[user]: ScoringModel
            Returns a scaled user model
        global_model: ScoringModel
            Returns a global scoring model
        """
        raise NotImplementedError
        
    def to_json(self):
        return (type(self).__name__, )
        
    def __str__(self):
        return type(self).__name__
