from solidago.poll_functions import (
    Sequential, LipschiTrust, FlexibleGeneralizedBradleyTerry, AffineOvertrust, Mehestan, 
    LipschitzStandardize, LipschitzQuantileShift, EntitywiseQrQuantile, Squash
)
from solidago.poll_functions.preference_learning.gbt.root_law import Uniform
from solidago.primitives.minimizer import SciPyMinimizer
from solidago.primitives.uncertainty import NLLIncrease


_modules = [
    LipschiTrust(pretrust_value=0.8, decay=0.8, sink_vouch=5.0, error=1.0e-8),
    FlexibleGeneralizedBradleyTerry(
        prior_stds=dict(directs=7., thresholds=7., categories=7., parameters=7.),
        minimizer=SciPyMinimizer(method="L-BFGS-B", convergence_error=1e-5),
        uncertainty=NLLIncrease(nll_increase=1., error=1e-1, max=1e3),
        comparison_root_law=Uniform(),
        discard_ratings=True
    ),
    AffineOvertrust(privacy_penalty=0.5, min_overtrust=2., overtrust_ratio=.1),
    Mehestan(
        lipschitz=1., min_scaler_activity=1., n_scalers_max=100, 
        privacy_penalty=.5, user_comparison_lipschitz=10., 
        p_norm_for_multiplicative_resilience=4., 
        n_entity_to_fully_compare_max=100, n_diffs_sample_max=1000,
        default_multiplier_dev=.5, default_translation_dev=1., error=1e-2
    ),
    LipschitzStandardize(dev_quantile=.9, lipschitz=10., error=1e-2, n_sampled_entities_per_user=100),
    LipschitzQuantileShift(quantile=.15, lipschitz=10., error=1e-2, target_score=.21, n_sampled_entities_per_user=100),
    EntitywiseQrQuantile(quantile=.2, lipschitz=.1, error=1e-5),
    Squash(score_max=100)
]

class TournesolFull(Sequential):
    def __init__(self, max_workers: int = 1, seed: int | None = None):
        super().__init__(_modules, "TournesolFull", max_workers, seed)
