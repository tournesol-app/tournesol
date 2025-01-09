import pytest
import pandas as pd

from solidago import *
from pandas import DataFrame

states = [ State.load(f"tests/pipeline/saved_{seed}") for seed in range(5) ]


@pytest.mark.parametrize("GBT", [NumbaUniformGBT])
def test_gbt_score_zero(GBT):
    
    if GBT == LBFGSUniformGBT:
        pytest.importorskip("torch")
        
    entities=Entities(["entity_1", "entity_2", "entity_3"])
    entity_name2index = { str(entity): index for index, entity in enumerate(entities) }
    comparisons=Comparisons(
        DataFrame([
            ["entity_1", "entity_2", 0, 10],
            ["entity_1", "entity_3", 0, 10],
        ], columns=["left_name", "right_name", "comparison", "comparison_max"]), 
        key_names=["left_name", "right_name"]
    )
    init_multiscores = MultiScore(key_names=["entity_name"])
    
    scores = NumbaUniformGBT().compute_scores(entities, entity_name2index, comparisons, init_multiscores)
    
    assert scores[0].value == pytest.approx((0, 1.8, 1.8), abs=0.1)
    assert scores[1].value == pytest.approx((0, 2.7, 2.7), abs=0.1)
    assert scores[2].value == pytest.approx((0, 2.7, 2.7), abs=0.1)


# @pytest.mark.parametrize("seed", range(4))
# def test_uniform_gbt(seed):
    # s = states[seed]
    # for optimizer in (UniformGBT, LBFGSUniformGBT):
        # preference_learn = optimizer(
            # prior_std_dev=7,
            # convergence_error=1e-5,
            # cumulant_generating_function_error=1e-5,
            # high_likelihood_range_threshold=1.
        # )
        # user_models[optimizer] = preference_learn(s.judgments, s.users, s.entities)
    # for user in s.users:
        # for entity in s.entities:
            # for criterion, score in user_models[UniformGBT][user](entity):
                # lbfgs_score = user_models[LBFGSUniformGBT][user](entity)[criterion]
                # assert score.value == pytest.approx(lbfgs_score.value, abs=1e-1)
                # assert score.left_unc == pytest.approx(lbfgs_score.left_unc, abs=1e-1)
                # assert score.right_unc == pytest.approx(lbfgs_score.right_unc, abs=1e-1)

