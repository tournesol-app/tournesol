import pytest
import numpy as np

from solidago import *
from solidago.modules.scaling import Mehestan, LipschitzStandardize, LipschitzQuantileShift

polls = [ Poll.load(f"tests/saved/{seed}") for seed in range(5) ]


@pytest.mark.parametrize("seed", range(5))
def test_learned_models(seed):
    mehestan = Mehestan(
        lipschitz=1., 
        min_scaler_activity=1.,
        n_scalers_max=5, 
        privacy_penalty=0.5,
        user_comparison_lipschitz=10.,
        p_norm_for_multiplicative_resilience=4.0,
        n_entity_to_fully_compare_max=100,
        error=1e-5,
        max_workers=1
    )
    s = polls[seed]
    users, entities, made_public = s.users, s.entities, s.made_public
    base_models = UserModels(s.user_models.user_directs)
    users, scaled_models = mehestan(users, entities, made_public, base_models)

@pytest.mark.parametrize("seed", range(5))
def test_standardize(seed):
    standardize = LipschitzStandardize(
        dev_quantile=0.9, 
        lipschitz=10.0, 
        error=1e-05,
        max_workers=1
    )
    base_models = UserModels(polls[seed].user_models.user_directs)
    standardized_models = standardize(polls[seed].entities, base_models)
    values = np.array([s.value for _, s in standardized_models()])
    deviations = np.abs(values - np.median(values))
    quantile = int(0.9 * len(deviations))
    assert deviations[np.argsort(deviations)[quantile]] < 2
    assert deviations[np.argsort(deviations)[quantile]] > 0.5
    
@pytest.mark.parametrize("seed", range(5))
def test_quantile_shift(seed):
    quantile_shift = LipschitzQuantileShift(
        quantile=0.15, 
        lipschitz=10.0, 
        error=1e-05,
        target_score=0.21,
        max_workers=1
    )
    base_models = UserModels(polls[seed].user_models.user_directs)
    shifted_models = quantile_shift(polls[seed].entities, base_models)
    assert np.median([s.value for _, s in shifted_models()]) > 0
