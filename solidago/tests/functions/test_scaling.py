import pytest
import numpy as np

from solidago import *
from solidago.functions.scaling import Mehestan, LipschitzStandardize, LipschitzQuantileShift

N_SEEDS = 3

polls = [ Poll.load(f"tests/saved/{seed}") for seed in range(N_SEEDS) ]


@pytest.mark.parametrize("seed", range(N_SEEDS))
def test_learned_models(seed):
    s = polls[seed]
    users, entities, made_public = s.users, s.entities, s.made_public
    base_models = UserModels(user_directs=s.user_models.user_directs)
    scaled_users, scaled = Mehestan()(users, entities, made_public, base_models)
    assert len(scaled_users) == len(users)
    assert len(base_models) == len(scaled)

@pytest.mark.parametrize("seed", range(N_SEEDS))
def test_standardize(seed):
    base_models = UserModels(user_directs=polls[seed].user_models.user_directs)
    standardized_models = LipschitzStandardize(lipschitz=1000)(polls[seed].entities, base_models)
    values = np.array([s.value for _, s in standardized_models()])
    deviations = np.abs(values - np.median(values))
    quantile = int(0.9 * len(deviations))
    assert deviations[np.argsort(deviations)[quantile]] < 3
    assert deviations[np.argsort(deviations)[quantile]] > 0.5
    
@pytest.mark.parametrize("seed", range(N_SEEDS))
def test_quantile_shift(seed):
    quantile_shift = LipschitzQuantileShift(lipschitz=1000)
    base_models = UserModels(user_directs=polls[seed].user_models.user_directs)
    shifted_models = quantile_shift(polls[seed].entities, base_models)
    assert np.median([s.value for _, s in shifted_models()]) > 0
