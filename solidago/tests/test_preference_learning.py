import pandas as pd
import pytest

import solidago.generative_model.test_data as td

@pytest.mark.parametrize("test", range(5))
def test_uniform_gbt(test):
    models = {
        user: td.pipeline.preference_learning(td.judgments[test][user], td.entities[test])
        for user, _ in td.users[test].iterrows()
    }
    for user in td.users[test].index:
        for entity in td.entities[test].index:
            output = models[user](entity)
            target = td.preference_learned_models[test][user](entity)
            assert output == pytest.approx(target, abs=1e-2), (user, entity)

