import pytest

from solidago import *
from solidago.functions.preference_learning import NumbaUniformGBT, LBFGSUniformGBT


@pytest.mark.parametrize("GBT", [NumbaUniformGBT, LBFGSUniformGBT])
def test_gbt_score_zero(GBT):
    
    if GBT == LBFGSUniformGBT:
        pytest.importorskip("torch")
        
    entities=Entities(["entity_1", "entity_2", "entity_3"])
    comparisons=Comparisons(["entity_name", "other_name"])
    comparisons["entity_1", "entity_2"] = Comparison(0, 10)
    comparisons["entity_1", "entity_3"] = Comparison(0, 10)
    
    scores = GBT(max_workers=2).user_learn_criterion(entities, comparisons)
    
    assert scores["entity_1"].to_triplet() == pytest.approx((0, 1.8, 1.8), abs=0.1)
    assert scores["entity_2"].to_triplet() == pytest.approx((0, 2.7, 2.7), abs=0.1)
    assert scores["entity_3"].to_triplet() == pytest.approx((0, 2.7, 2.7), abs=0.1)
    
    
@pytest.mark.parametrize("GBT", [NumbaUniformGBT, LBFGSUniformGBT])
def test_gbt_score_monotonicity(GBT):
    
    if GBT == LBFGSUniformGBT:
        pytest.importorskip("torch")
        
    entities = Entities(["entity_1", "entity_2", "entity_3"])
    comparisons = Comparisons(["entity_name", "other_name"])
    comparisons["entity_1", "entity_2"] = Comparison(5, 10)
    comparisons["entity_1", "entity_3"] = Comparison(2, 10)
    
    scores = GBT(max_workers=2).user_learn_criterion(entities, comparisons)
    
    assert scores["entity_1"].value < scores["entity_3"].value
    assert scores["entity_3"].value < scores["entity_2"].value
    assert scores["entity_1"].left_unc > scores["entity_1"].right_unc
    assert scores["entity_2"].left_unc < scores["entity_2"].right_unc


def test_uniform_gbt():
    poll = Poll.load(f"tests/saved/0")
    kwargs = dict(prior_std=7.0, uncertainty_nll_increase=1.0, max_uncertainty=1e3, max_workers=1)
    GBTs = (NumbaUniformGBT, LBFGSUniformGBT)
    user_models_tuple = tuple(GBT(**kwargs).poll2objects_function(poll) for GBT in GBTs)
    for user in poll.users:
        for entity in poll.entities:
            for (criterion,), score in user_models_tuple[0][2][user](entity):
                lbfgs_score = user_models_tuple[1][2][user](entity, criterion)
                args = (str(user), str(entity), criterion, score, lbfgs_score)
                assert score.to_triplet() == pytest.approx(lbfgs_score.to_triplet(), abs=5e-1), args

