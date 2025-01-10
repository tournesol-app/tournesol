import pytest
import pandas as pd

from solidago import *
from pandas import DataFrame

states = [ State.load(f"tests/pipeline/saved_{seed}") for seed in range(5) ]


@pytest.mark.parametrize("GBT", [NumbaUniformGBT, LBFGSUniformGBT])
def test_gbt_score_zero(GBT):
    
    if GBT == LBFGSUniformGBT:
        pytest.importorskip("torch")
        
    entities=Entities(["entity_1", "entity_2", "entity_3"])
    comparisons=Comparisons(
        DataFrame([
            ["entity_1", "entity_2", 0, 10],
            ["entity_1", "entity_3", 0, 10],
        ], columns=["left_name", "right_name", "comparison", "comparison_max"]), 
        key_names=["left_name", "right_name"]
    )
    init_multiscores = MultiScore(key_names=["entity_name"])
    
    scores = NumbaUniformGBT().user_learn_criterion(entities, comparisons, init_multiscores)
    
    assert scores["entity_1"].to_triplet() == pytest.approx((0, 1.8, 1.8), abs=0.1)
    assert scores["entity_2"].to_triplet() == pytest.approx((0, 2.7, 2.7), abs=0.1)
    assert scores["entity_3"].to_triplet() == pytest.approx((0, 2.7, 2.7), abs=0.1)
    
    
@pytest.mark.parametrize("GBT", [NumbaUniformGBT, LBFGSUniformGBT])
def test_gbt_score_monotonicity(GBT):
    
    if GBT == LBFGSUniformGBT:
        pytest.importorskip("torch")
        
    entities=Entities(["entity_1", "entity_2", "entity_3"])
    comparisons=Comparisons(
        DataFrame([
            ["entity_1", "entity_2", 5, 10],
            ["entity_1", "entity_3", 2, 10],
        ], columns=["left_name", "right_name", "comparison", "comparison_max"]), 
        key_names=["left_name", "right_name"]
    )
    init_multiscores = MultiScore(key_names=["entity_name"])
    
    scores = NumbaUniformGBT().user_learn_criterion(entities, comparisons, init_multiscores)
    
    assert scores["entity_1"].value < scores["entity_3"].value
    assert scores["entity_3"].value < scores["entity_2"].value


# @pytest.mark.parametrize("seed", range(4))
# def test_uniform_gbt(seed):
    # s = states[seed]
    # for optimizer in (NumbaUniformGBT, LBFGSUniformGBT):
        # preference_learning = optimizer(
            # prior_std_dev=7.0,
            # uncertainty_nll_increase=1.0,
            # max_uncertainty=1e3,
            # last_comparison_only=True,
        # )
        # user_models[optimizer] = preference_learning.state2objects_function(s)
    # for user in s.users:
        # for entity in s.entities:
            # for criterion, score in user_models[UniformGBT][user](entity):
                # lbfgs_score = user_models[LBFGSUniformGBT][user](entity)[criterion]
                # assert score.to_triplet() == pytest.approx(lbfgs_score.to_triplet(), abs=1e-1)

