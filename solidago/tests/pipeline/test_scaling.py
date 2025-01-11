import pytest
import numpy as np

from solidago import *

states = [ State.load(f"tests/pipeline/saved/{seed}") for seed in range(5) ]


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
        error=1e-5
    )
    s = states[seed]
    users, entities, made_public = s.users, s.entities, s.made_public
    base_models = UserModels({ username: model.base_model()[0] for username, model in s.user_models })
    users, scaled_models = mehestan(users, entities, made_public, base_models)
    
@pytest.mark.parametrize("seed", range(5))
def test_standardize(seed):
    standardize = LipschitzStandardize(
        dev_quantile=0.9, 
        lipschitz=10.0, 
        error=1e-05
    )
    s = states[seed]
    standardized_models = standardize.state2objects_function(states[seed])
    assert standardized_models.score(states[seed].entities).to_df()["score"].std() < 2
    assert standardized_models.score(states[seed].entities).to_df()["score"].std() > 0.5
    
@pytest.mark.parametrize("seed", range(5))
def test_quantile_shift(seed):
    quantile_shift = LipschitzQuantileShift(
        quantile=0.15, 
        lipschitz=10.0, 
        error=1e-05,
        target_score=0.21,
    )
    shifted_models = quantile_shift.state2objects_function(states[seed])
    assert shifted_models.score(states[seed].entities).to_df()["score"].median() > 0
