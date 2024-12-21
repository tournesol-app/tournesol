import pandas as pd

from .base import Scaling

from solidago.privacy_settings import PrivacySettings
from solidago.scoring_model import ScoringModel, ScaledScoringModel
from solidago.voting_rights import VotingRights
from solidago.primitives import qr_standard_deviation


class Standardize(Scaling):
    def __init__(self, dev_quantile: float=0.9, lipschitz: float=0.1, error: float=1e-5):
        """ The scores are shifted so that their quantile zero_quantile equals zero
        
        Parameters
        ----------
        zero_quantile: float
        """
        self.dev_quantile = dev_quantile
        self.lipschitz = lipschitz
        self.error = error

    def __call__(
        self, 
        user_models: dict[int, ScoringModel],
        users: pd.DataFrame,
        entities: pd.DataFrame,
        voting_rights: VotingRights,
        privacy: PrivacySettings
    ):
        df = _get_user_scores(user_models, entities)
        std_dev = self._compute_std_dev(df)
        return {
            user: ScaledScoringModel(user_model, multiplicator=1/std_dev)
            for (user, user_model) in user_models.items()
        }

    def _compute_std_dev(self, df):
        w = 1 / df.groupby("user_id")["scores"].transform("size")
        return qr_standard_deviation(
            lipschitz=self.lipschitz,
            values=df["scores"].to_numpy(),
            quantile_dev=self.dev_quantile,
            voting_rights=w.to_numpy(),
            left_uncertainties=df["left_uncertainties"].to_numpy(),
            right_uncertainties=df["right_uncertainties"].to_numpy(),
            default_dev=1.0,
            error=self.error,
        )

    def to_json(self):
        return type(self).__name__, dict(dev_quantile=self.dev_quantile, 
            lipschitz=self.lipschitz, error=self.error)

    def __str__(self):
        prop_names = ["dev_quantile", "lipschitz", "error"]
        prop = ", ".join([f"{p}={getattr(self, p)}" for p in prop_names])
        return f"{type(self).__name__}({prop})"


def _get_user_scores(user_models: dict[int, ScoringModel], entities: pd.DataFrame):
    user_list, entity_list = list(), list()
    scores, lefts, rights = list(), list(), list()
    for user_id, scoring_model in user_models.items():
        for entity_id, output in scoring_model.iter_entities(entities):
            user_list.append(user_id)
            entity_list.append(entity_id)
            scores.append(output[0])
            lefts.append(output[1])
            rights.append(output[2])

    return pd.DataFrame(
        dict(
            user_id=user_list,
            entity_id=entity_list,
            scores=scores,
            left_uncertainties=lefts,
            right_uncertainties=rights,
        )
    )
