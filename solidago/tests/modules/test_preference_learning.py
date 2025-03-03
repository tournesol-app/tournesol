import pytest

from solidago import *
from solidago.modules.preference_learning import NumbaUniformGBT, LBFGSUniformGBT
from pandas import DataFrame


@pytest.mark.parametrize("GBT", [NumbaUniformGBT, LBFGSUniformGBT])
def test_gbt_score_zero(GBT):
    
    if GBT == LBFGSUniformGBT:
        pytest.importorskip("torch")
        
    entities=Entities(["entity_1", "entity_2", "entity_3"])
    comparisons=Comparisons(
        DataFrame([
            ["entity_1", "entity_2", 0, 10],
            ["entity_1", "entity_3", 0, 10],
        ], columns=["left_name", "right_name", "value", "max"]), 
        key_names=["left_name", "right_name"]
    )
    init_multiscores = MultiScore(key_names=["entity_name"])
    
    scores = NumbaUniformGBT().user_learn_criterion(entities, comparisons, init_multiscores)
    
    assert scores.get("entity_1").to_triplet() == pytest.approx((0, 1.8, 1.8), abs=0.1)
    assert scores.get("entity_2").to_triplet() == pytest.approx((0, 2.7, 2.7), abs=0.1)
    assert scores.get("entity_3").to_triplet() == pytest.approx((0, 2.7, 2.7), abs=0.1)
    
    
@pytest.mark.parametrize("GBT", [NumbaUniformGBT, LBFGSUniformGBT])
def test_gbt_score_monotonicity(GBT):
    
    if GBT == LBFGSUniformGBT:
        pytest.importorskip("torch")
        
    entities=Entities(["entity_1", "entity_2", "entity_3"])
    comparisons=Comparisons(
        DataFrame([
            ["entity_1", "entity_2", 5, 10],
            ["entity_1", "entity_3", 2, 10],
        ], columns=["left_name", "right_name", "value", "max"]), 
        key_names=["left_name", "right_name"]
    )
    init_multiscores = MultiScore(key_names=["entity_name"])
    
    scores = GBT().user_learn_criterion(entities, comparisons, init_multiscores)
    
    assert scores.get("entity_1").value < scores.get("entity_3").value
    assert scores.get("entity_3").value < scores.get("entity_2").value
    assert scores.get("entity_1").left_unc > scores.get("entity_1").right_unc
    assert scores.get("entity_2").left_unc < scores.get("entity_2").right_unc


def test_uniform_gbt():
    s = State.load(f"tests/saved/0")
    user_models = dict()
    for index, optimizer in enumerate((NumbaUniformGBT, LBFGSUniformGBT)):
        preference_learning = optimizer(
            prior_std_dev=7.0,
            uncertainty_nll_increase=1.0,
            max_uncertainty=1e3,
            last_comparison_only=True,
        )
        user_models[index] = preference_learning.state2objects_function(s)
    for user in s.users:
        for entity in s.entities:
            for criterion, score in user_models[0][user](entity):
                lbfgs_score = user_models[1][user](entity).get(criterion)
                assert score.to_triplet() == pytest.approx(lbfgs_score.to_triplet(), abs=2e-1)

