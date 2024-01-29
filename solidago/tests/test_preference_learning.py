import pytest
import importlib
import pandas as pd
import numpy as np

@pytest.mark.parametrize("test", range(4))
def test_uniform_gbt(test):
    td = importlib.import_module(f"data.data_{test}")
    models = td.pipeline.preference_learning(td.judgments, td.users, td.entities)
    for user in td.users.index:
        for entity in td.entities.index:
            output = models[user](entity)
            target = td.learned_models[user](entity, td.entities.loc[entity])
            assert output == pytest.approx(target, abs=1e-1), (user, entity)

