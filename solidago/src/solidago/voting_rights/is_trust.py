import pandas as pd

from solidago.scoring_model import ScoringModel
from .voting_rights import VotingRights
from .base import PrivacySettings, VotingRightsAssignment


class IsTrust(VotingRightsAssignment):
    def __init__(self, privacy_penalty: float = 0.5):
        self.privacy_penalty = privacy_penalty

    def __call__(
        self,
        users: pd.DataFrame,
        entities: pd.DataFrame,
        vouches: pd.DataFrame,
        privacy: PrivacySettings,
        user_models: dict[int, ScoringModel],
    ) -> tuple[VotingRights, pd.DataFrame]:
        """Compute voting rights

        Parameters
        ----------
        users: DataFrame with columns
            * user_id (int, index)
            * trust_score (float)
        entities: DataFrame with columns
            * entity_id (int, index)
        vouches: Not used
        privacy: PrivacySettings
            privacy[user, entity] in { True, False, None }
        user_models: Invidiual scoring model per user

        Returns
        -------
        voting_rights[user, entity] is the voting right
            of a user on entity for criterion
        entities: DataFrame with columns
            * entity_id (int, index)
        """
        voting_rights = VotingRights()

        for user, model in user_models.items():
            for entity in model.scored_entities():
                is_private = privacy[user, entity] == True
                voting_rights[user, entity] = (
                    is_private * self.privacy_penalty * users.loc[user, "trust_score"]
                )

        return voting_rights, entities

    def to_json(self):
        return (type(self).__name__,)
