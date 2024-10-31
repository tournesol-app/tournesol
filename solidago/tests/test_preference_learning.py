import pandas as pd
import pytest
import importlib


import solidago.preference_learning as preference_learning


@pytest.mark.parametrize("test", range(4))
def test_uniform_gbt(test):
    td = importlib.import_module(f"data.data_{test}")
    models = td.pipeline.preference_learning(td.judgments, td.users, td.entities)
    for user in td.users.index:
        for entity in td.entities.index:
            output = models[user](entity)
            target = td.learned_models[user](entity, td.entities.loc[entity])
            assert output == pytest.approx(target, abs=1e-1), (user, entity)


@pytest.mark.parametrize("test", range(4))
def test_lbfgs_uniform_gbt(test):
    pytest.importorskip("torch")
    LBFGSUniformGBT = preference_learning.LBFGSUniformGBT
    td = importlib.import_module(f"data.data_{test}")
    models = LBFGSUniformGBT()(td.judgments, td.users, td.entities)
    for user in td.users.index:
        for entity in td.entities.index:
            output = models[user](entity)
            target = td.learned_models[user](entity, td.entities.loc[entity])
            assert output == pytest.approx(target, abs=1e-1), (user, entity)


@pytest.mark.parametrize("method", ["UniformGBT", "LBFGSUniformGBT"])
def test_gbt_score_zero(method):
    if method == "LBFGSUniformGBT":
        pytest.importorskip("torch")
    gbt = getattr(preference_learning, method)()
    model = gbt.comparison_learning(
        comparisons=pd.DataFrame(
            {
                "entity_a": [1, 1],
                "entity_b": [2, 3],
                "comparison": [0, 0],
                "comparison_max": [10, 10],
            }
        )
    )

    assert model(entity_id=1) == pytest.approx((0, 1.8, 1.8), abs=0.1)
    assert model(entity_id=2) == pytest.approx((0, 2.7, 2.7), abs=0.1)
    assert model(entity_id=3) == pytest.approx((0, 2.7, 2.7), abs=0.1)
