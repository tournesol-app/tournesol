import p

from . import Scaling

from solidago.privacy_settings import PrivacySettings
from solidago.scoring_model import ScoringModel
from solidago.primitives import QrQuantile


class QuantileZeroShift(Scaling):
    def __init__(self, zero_quantile: float=0.15, lipschitz: float=0.1, error: float=1e-5):
        """ The scores are shifted so that their quantile zero_quantile equals zero
        
        Parameters
        ----------
        zero_quantile: float
        """
        self.zero_quantile = zero_quantile
        self.lipschitz = lipschitz
        self.error = error
    
    def __call__(
        self, 
        user_models: dict[int, ScoringModel],
        users: pd.DataFrame,
        entities: pd.DataFrame,
        voting_rights: VotingRights,
        privacy: PrivacySettings
    ) -> dict[int, ScoringModel]:
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
        scores, lefts, rights = list(), list(), list()
        for user in user_models:
            for entity, row in entities.iterrows():
                output = user_models[user](entity, row)
                if output is not None:
                    scores.append(output[0])
                    lefts.append(output[1])
                    rights.append(output[2])
        
        shift = qr_quantile(self.lipschitz, self.zero_quantile, scores, 
            voting_rights, lefts, rights, error=self.error)
        
        return {
            user: ScaledScoringModel(user_models[user], translation=shift)
            for user in user_models
        }
