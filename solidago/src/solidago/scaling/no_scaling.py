import pandas as pd

from solidago.voting_rights import VotingRights
from solidago.privacy_settings import PrivacySettings
from solidago.scoring_model import ScoringModel, ScaledScoringModel

from .base import Scaling

class NoScaling(Scaling):
    def __call__(
        self, 
        user_models: dict[int, ScoringModel],
        users: pd.DataFrame = ...,
        entities: pd.DataFrame = ...,
        voting_rights: VotingRights = ...,
        privacy: PrivacySettings = ...,
    ) -> dict[int, ScaledScoringModel]:
        """ Returns scaled user models
        
        Parameters
        ----------
        user_models: dict[int, ScoringModel]
            user_models[user] is user's scoring model
        users: DataFrame with columns
            * user_id (int, index)
            * trust_score (float)
        entities: DataFrame with columns
            * entity_id (int, ind)
        voting_rights: VotingRights
            voting_rights[user, entity]: float
        privacy: PrivacySettings
            privacy[user, entity] in { True, False, None }

        Returns
        -------
        out[user]: ScoringModel
            Will be scaled by the Scaling method
        """
        return {
            user_id: ScaledScoringModel(scoring)
            for (user_id, scoring) in user_models.items()
        }
