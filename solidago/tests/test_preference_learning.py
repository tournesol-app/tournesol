import pytest
import importlib
import pandas as pd

@pytest.mark.parametrize("test", range(5))
def test_uniform_gbt(test):
    td = importlib.import_module(f"data.data_{test}")
    models = {
        user: td.pipeline.preference_learning(td.judgments[user], td.entities)
        for user, _ in td.users.iterrows()
    }
    for user in td.users.index:
        for entity in td.entities.index:
            output = models[user](entity)
            target = td.learned_models[user](entity, td.entities.loc[entity])
            assert output == pytest.approx(target, abs=1e-2), (user, entity)

