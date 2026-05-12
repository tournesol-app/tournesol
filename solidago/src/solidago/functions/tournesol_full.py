from typing import TYPE_CHECKING

from solidago.functions.sequential import Sequential
from solidago.functions.poll_function import PollFunction
from solidago.primitives.minimizer import SciPyMinimizer
from solidago.primitives.uncertainty import NLLIncrease

if TYPE_CHECKING:
    from solidago.functions import simple_stats


class TournesolFull(Sequential):
    def __init__(self, max_workers: int = 1, seed: int | None = None):
        import solidago.functions as f
        subfunctions = [
            f.simple_stats.SimpleUserStats(max_workers=max_workers),
            f.simple_stats.SimpleEntityStats(max_workers=max_workers),
            f.trust_propagation.LipschiTrust(
                pretrust_value=0.8, decay=0.8, sink_vouch=5.0, 
                error=1.0e-8, max_workers=max_workers
            ),
            f.preference_learning.FlexibleGeneralizedBradleyTerry(
                prior_stds=dict(directs=7., thresholds=7., categories=7., parameters=7.),
                minimizer=SciPyMinimizer(method="L-BFGS-B", convergence_error=1e-5),
                uncertainty=NLLIncrease(nll_increase=1., error=1e-1, max=1e3),
                comparison_root_law="Uniform",
                discard_ratings=True,
                max_workers=max_workers,
            ),
            f.voting_rights.AffineOvertrust(
                privacy_penalty=0.5, min_overtrust=2., overtrust_ratio=.1, 
                max_workers=max_workers
            ),
            f.scaling.Mehestan(
                lipschitz=1., min_scaler_activity=1., n_scalers_max=100, 
                privacy_penalty=.5, user_comparison_lipschitz=10., 
                p_norm_for_multiplicative_resilience=4., 
                n_entity_to_fully_compare_max=100, n_diffs_sample_max=1000,
                default_multiplier_dev=.5, default_translation_dev=1., 
                error=1e-2, max_workers=max_workers
            ),
            f.scaling.LipschitzStandardize(
                dev_quantile=.9, lipschitz=10., error=1e-2, 
                n_sampled_entities_per_user=100, max_workers=max_workers
            ),
            f.scaling.LipschitzQuantileShift(
                quantile=.15, lipschitz=10., error=1e-2, target_score=.21, 
                n_sampled_entities_per_user=100, max_workers=max_workers
            ),
            f.aggregation.EntitywiseQrQuantile(
                quantile=.2, lipschitz=.1, error=1e-5, max_workers=max_workers
            ),
            f.post_process.Squash(score_max=100, max_workers=max_workers)
        ]
        super().__init__(subfunctions, "TournesolFull", max_workers, seed)

    @property
    def simple_user_stats(self) -> "simple_stats.SimpleUserStats":
        return self[0] # type: ignore

    @property
    def simple_entity_stats(self) -> "simple_stats.SimpleEntityStats":
        return self[1] # type: ignore

    @property
    def trust_propagation(self) -> PollFunction:
        return self[2]

    @property
    def preference_learning(self) -> PollFunction:
        return self[3]

    @property
    def voting_right_assignment(self) -> PollFunction:
        return self[4]

    @property
    def mehestan(self) -> PollFunction:
        return self[5]

    @property
    def standardize(self) -> PollFunction:
        return self[6]

    @property
    def quantile_shift(self) -> PollFunction:
        return self[7]
    
    @property
    def scale(self) -> PollFunction:
        return Sequential([self.mehestan, self.standardize, self.quantile_shift], "scale", self.max_workers, self.seed)

    @property
    def aggregate(self) -> PollFunction:
        return self[8]

    @property
    def post_process(self) -> PollFunction:
        return self[9]