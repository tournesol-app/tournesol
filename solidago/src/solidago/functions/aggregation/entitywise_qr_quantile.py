import numpy as np
from numpy.typing import NDArray

from solidago.primitives.lipschitz import qr_quantile, qr_uncertainty
from solidago.poll import *
from solidago.functions.aggregation.entity_criterion_wise import EntityCriterionWise


class EntitywiseQrQuantile(EntityCriterionWise):
    note: str = "entitywise_qr_quantile"
    parallelize: bool = False

    def __init__(
        self,
        quantile: float = 0.2,
        lipschitz: float = 0.1,
        error: float = 1e-5,
        scale_uncertainty_by_voting_rights=False,
        *args,
        **kwargs,
    ):
        """Aggregates scores using the quadratically regularized quantile
        for each entity and each criterion.

        Parameters
        ----------
        quantile: float
            Quantile of the scores to compute, between 0 and 1.
            With 0.5, the aggregate is the quadratically regularized median.
        lipschitz: float
            Lipschitz parameter of the quadratic regularization.
        error: float
            Numerical error tolerance of the quantile computation.
        scale_uncertainty_by_voting_rights: bool
            EXPERIMENTAL
            If True, divides the uncertainty by the square root of the sum of
            voting rights. This treats voting rights as a measure of evidence,
            so uncertainty shrinks as ~1/sqrt(n) with the number of full-voter equivalents.
            If False, the raw uncertainty from `qr_uncertainty` is returned.
        """
        super().__init__(*args, **kwargs)
        self.quantile = quantile
        self.lipschitz = lipschitz
        self.error = error
        self.scale_uncertainty_by_voting_rights = scale_uncertainty_by_voting_rights

    def _args(self, # type: ignore
        variable: tuple[Entity, str], 
        nonargs, # score: Scores, with keynames == ["username"]
        voting_rights: VotingRights,
    ) -> tuple[NDArray, NDArray, NDArray, NDArray, float, float, float]:
        return *super()._args(variable, nonargs, voting_rights), self.lipschitz, self.error, self.quantile

    def thread_function(
        self,
        vrights: NDArray,
        values: NDArray,
        lefts: NDArray,
        rights: NDArray,
        lipschitz: float,
        error: float,
        quantile: float,
    ) -> tuple[float, float, float]:
        if len(values) == 0:
            return np.nan, np.inf, np.inf
        kwargs = dict(lipschitz=lipschitz, error=error, voting_rights=vrights)
        kwargs |= dict(values=values, left_unc=lefts, right_unc=rights)
        quantile_score = qr_quantile(quantile=quantile, **kwargs)  # type: ignore
        median = quantile_score if quantile == 0.5 else None
        uncertainty = qr_uncertainty(default_dev=1.0, median=median, **kwargs)  # type: ignore
        if self.scale_uncertainty_by_voting_rights:
            uncertainty /= np.sqrt(vrights.sum())
        return quantile_score, uncertainty, uncertainty
