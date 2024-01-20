import pandas as pd
import pytest

import solidago.generative_model.test_data as td

@pytest.mark.parametrize("test", range(5))
def test_uniform_gbt(test):
    learned_user_models = [
    {
        user: td.pipeline.preference_learning(td.judgments[test][user], td.entities[test])
        for user, _ in td.users[test].iterrows()
    } 
    # assert learned_user_models[4][23](8, pd.Series()) == user_models[4][23](8, pd.Series())
]


