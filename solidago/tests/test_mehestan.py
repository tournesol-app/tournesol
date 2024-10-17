import pytest
import importlib
import pandas as pd
import numpy as np

from solidago.voting_rights import VotingRights
from solidago.privacy_settings import PrivacySettings
from solidago.scoring_model import DirectScoringModel, ScaledScoringModel

from solidago.scaling import Mehestan

from solidago.scaling.mehestan import (Mehestan, _aggregate_user_comparisons, _aggregate)


mehestan = Mehestan(
    lipschitz=100., 
    min_activity=1.0,
    n_scalers_max=3, 
    privacy_penalty=0.5,
    user_comparison_lipschitz=100.,
    p_norm_for_multiplicative_resilience=4.0,
    error=1e-5
)

@pytest.mark.parametrize("test", range(5))
def test_learned_models(test):
    td = importlib.import_module(f"data.data_{test}")
    if "trust_score" not in td.users:
        td.users["trust_score"] = 1.0
    m_models = mehestan(td.learned_models, td.users, td.entities, td.voting_rights, td.privacy)
