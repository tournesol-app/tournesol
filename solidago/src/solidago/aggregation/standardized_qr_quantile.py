import pandas as pd
import numpy as np

from .base import Aggregation

from solidago.voting_rights import VotingRights
from solidago.scoring_model import ScoringModel, DirectScoringModel, ScaledScoringModel

from solidago.primitives import qr_quantile, qr_standard_deviation, qr_uncertainty


class StandardizedQrQuantile(Aggregation):
    def __init__(self, quantile=0.2, dev_quantile=0.9, lipschitz=0.1, error=1e-5):
        """ Standardize scores so that only a fraction 1 - dev_quantile
        of the scores is further than 1 away from the median,
        and then run qr_median to aggregate the scores.
        
        Parameters
        ----------
        qtl_std_dev: float
        lipschitz: float
        error: float
        """
        self.quantile = quantile
        self.dev_quantile = dev_quantile
        self.lipschitz = lipschitz
        self.error = error
 
    def __call__(
        self, 
        voting_rights: VotingRights,
        user_models: dict[int, ScoringModel],
        users: pd.DataFrame,
        entities: pd.DataFrame
    ) -> tuple[dict[int, ScaledScoringModel], ScoringModel]:
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
        df = _get_user_scores(voting_rights, user_models, entities)
        std_dev = self._compute_std_dev(df)
            
        scaled_models = {
            user_id: ScaledScoringModel(scoring, 1/std_dev)
            for user_id, scoring in user_models.items()
        }
        for column in ("scores", "left_uncertainties", "right_uncertainties"):
            df[column] /= std_dev

        global_scores = DirectScoringModel()
        for entity_id, dfe in df.groupby("entity_id"):
            if entity_id not in entities.index:
                continue
            score = qr_quantile(
                self.lipschitz, 
                self.quantile, 
                np.array(dfe["scores"]), 
                np.array(dfe["voting_rights"]), 
                np.array(dfe["left_uncertainties"]),
                np.array(dfe["right_uncertainties"]),
                self.error
            )
            uncertainty = qr_uncertainty(
                self.lipschitz, 
                np.array(dfe["scores"]), 
                np.array(dfe["voting_rights"]), 
                np.array(dfe["left_uncertainties"]),
                np.array(dfe["right_uncertainties"]),
                default_dev = 1,
                error = self.error,
            )
            global_scores[entity_id] = score, uncertainty
        return scaled_models, global_scores
    
    def _compute_std_dev(self, df):
        if len(df) == 0:
            return 1.0
        return qr_standard_deviation(
            lipschitz=self.lipschitz,
            values=df["scores"].to_numpy(),
            quantile_dev=self.dev_quantile,
            voting_rights=df["voting_rights"].to_numpy(),
            left_uncertainties=df["left_uncertainties"].to_numpy(),
            right_uncertainties=df["right_uncertainties"].to_numpy(),
            default_dev=1.0,
            error=self.error
        )
    
    def to_json(self):
        return type(self).__name__, dict(
            quantile=self.quantile, dev_quantile=self.dev_quantile, 
            lipschitz=self.lipschitz, error=self.error
        )

    def __str__(self):
        prop_names = ["quantile", "dev_quantile", "lipschitz", "error"]
        prop = ", ".join([f"{p}={getattr(self, p)}" for p in prop_names])
        return f"{type(self).__name__}({prop})"


def _get_user_scores(
    voting_rights: VotingRights, user_models: dict[int, ScoringModel], entities: pd.DataFrame
):
    return pd.DataFrame(
        (
            dict(
                user_id=user_id,
                entity_id=entity_id,
                voting_rights=voting_rights[user_id, entity_id],
                scores=score,
                left_uncertainties=left,
                right_uncertainties=right,
            )
            for user_id, user_model in user_models.items()
            for entity_id, (score, left, right) in user_model.iter_entities(entities)
        ),
        columns=[
            "user_id",
            "entity_id",
            "voting_rights",
            "scores",
            "left_uncertainties",
            "right_uncertainties",
        ],
    )
