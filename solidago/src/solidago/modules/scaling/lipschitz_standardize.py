from solidago.primitives import qr_standard_deviation
from solidago.state import *
from solidago.modules.base import StateFunction


class LipschitzStandardize(StateFunction):
    def __init__(self, dev_quantile: float=0.9, lipschitz: float=0.1, error: float=1e-5):
        """ The scores are shifted so that their quantile zero_quantile equals zero
        
        Parameters
        ----------
        dev_quantile: float
        """
        self.dev_quantile = dev_quantile
        self.lipschitz = lipschitz
        self.error = error

    def __call__(self, entities: Entities, user_models: UserModels) -> UserModels:
        scores = user_models.score(entities) # key_names == ["username", "criterion", "entity_name"]
        scales = MultiScore(key_names=["depth", "kind", "criterion"])
        for criterion, user_scores in scores.to_dict(["criterion"]):
            weights = 1 / user_scores.groupby("username").transform("size")
            std_dev = qr_standard_deviation(
                lipschitz=self.lipschitz,
                values=user_scores["value"].to_numpy(),
                quantile_dev=self.dev_quantile,
                voting_rights=weights.to_numpy(),
                left_uncertainties=user_scores["left_unc"].to_numpy(),
                right_uncertainties=user_scores["right_unc"].to_numpy(),
                default_dev=1.0,
                error=self.error,
            )
            scales.set(0, "multiplier", criterion, 1/std_dev, 0, 0)
        return user_models.scale(scales, note="lipschitz_standardardize")
