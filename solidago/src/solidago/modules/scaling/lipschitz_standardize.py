import timeit
import logging
logger = logging.getLogger(__name__)

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
        scales = MultiScore(key_names=["depth", "kind", "criterion"])
        for criterion in user_models.criteria():
            logger.info(f"Lipschitz Standardize for criterion={criterion}")
            start = timeit.default_timer()
            scores = user_models(entities, criterion) # key_names == ["username", "entity_name"]
            end = timeit.default_timer()
            logger.info(f"    Computed all user scores in {int(end - start)} seconds for criterion={criterion}")
            start = end
            weights = 1 / scores.groupby("username").transform("size")
            end = timeit.default_timer()
            logger.info(f"    Computed weights in {int(end - start)} seconds for criterion={criterion}")
            start = end
            std_dev = qr_standard_deviation(
                lipschitz=self.lipschitz,
                values=scores["value"].to_numpy(),
                quantile_dev=self.dev_quantile,
                voting_rights=weights.to_numpy(),
                left_uncertainties=scores["left_unc"].to_numpy(),
                right_uncertainties=scores["right_unc"].to_numpy(),
                default_dev=1.0,
                error=self.error,
            )
            end = timeit.default_timer()
            logger.info(f"    Computed standard deviation in {int(end - start)} seconds for criterion={criterion}")
            scales.set(0, "multiplier", criterion, 1/std_dev, 0, 0)
        return user_models.scale(scales, note="lipschitz_standardardize")
