import pytest
import importlib
import pandas as pd
import numpy as np

from solidago.voting_rights import VotingRights
from solidago.privacy_settings import PrivacySettings
from solidago.judgments import DataFrameJudgments
from solidago.scoring_model import DirectScoringModel, ScaledScoringModel

from solidago.scaling import ScalingCompose, Mehestan, QuantileZeroShift

from solidago.scaling.mehestan import (Mehestan, _aggregate_user_comparisons, _aggregate)


mehestan = Mehestan(
    lipschitz=100., 
    min_activity=1, 
    n_scalers_max=3, 
    privacy_penalty=0.5,
    user_comparison_lipschitz=100.,
    p_norm_for_multiplicative_resilience=4.0,
    error=1e-5
)

@pytest.mark.parametrize("test", range(5))
def test_learned_models(test):
    td = importlib.import_module(f"data.data_{test}")
    m_models = mehestan(td.learned_models, td.users, td.entities, td.voting_rights, td.privacy)


users = pd.DataFrame(dict(
    is_pretrusted=[True] * 5,
    trust_score=[1.] * 5,
))
users.index.name = "user_id"

entities = pd.DataFrame(index=range(5))
entities.index.name = "entity_id"

privacy = PrivacySettings({
    0: { 0: False, 1: False, 2: False, 3: False, 4: False },
    1: { 0: False, 1: False, 2: False, 3: False, 4: False },
})

voting_rights = VotingRights({
    0: {0: 1.0, 1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0},
    1: {0: 1.0, 1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0},
    2: {0: 1.0, 1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0},
    3: {0: 1.0, 1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0},
    4: {0: 1.0, 1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0},
})

learned_models = {
    0: DirectScoringModel({
        0: (0., 0., 0.),
        1: (1., 0., 0.),
        2: (2., 0., 0.),
        3: (3., 0., 0.),
        4: (4., 0., 0.),
    }),
    1: DirectScoringModel({
        0: (0., 0., 0.),
        1: (5., 0., 0.),
        2: (10., 0., 0),
    }),
    2: DirectScoringModel({
        0: (-5., 0., 0.),
        1: (-6., 0., 0.),
        2: (-7., 0., 0.),
    }),
    3: DirectScoringModel({
        0: (0., 0., 0.),
        1: (4., 0., 0.),
    }),
    4: DirectScoringModel({
        0: (0., 0., 0.),
        2: (2., 0., 0.),
    })
} 

activities = mehestan.compute_activities(learned_models, entities, users, privacy)
is_scaler = mehestan.compute_scalers(learned_models, entities, users, privacy)
users = users.assign(is_scaler=is_scaler)
scalers = users[users["is_scaler"]]
nonscalers = users[users["is_scaler"] == False]
        
scaler_model_norms = mehestan.compute_model_norms(learned_models, scalers, entities, privacy)
scaler_entity_ratios = mehestan.compute_entity_ratios(learned_models, learned_models, entities, scalers, scalers, privacy)
scaler_ratio_voting_rights, scaler_ratios, scaler_ratio_uncertainties = _aggregate_user_comparisons(
    scalers, scaler_entity_ratios, 
    error=mehestan.error, lipschitz=mehestan.user_comparison_lipschitz
)
scaler_multiplicators = mehestan.compute_multiplicators(
    scaler_ratio_voting_rights, scaler_ratios, scaler_ratio_uncertainties, scaler_model_norms
)
scaler_entity_diffs = mehestan.compute_entity_diffs(
    learned_models, learned_models, scalers, scalers, entities, privacy, scaler_multiplicators
)
scaler_diff_voting_rights, scaler_diffs, scaler_diff_uncertainties = _aggregate_user_comparisons(
    scalers, scaler_entity_diffs,
    error=mehestan.error, lipschitz=mehestan.user_comparison_lipschitz
)
scaler_translations = mehestan.compute_translations(
    scaler_diff_voting_rights, scaler_diffs, scaler_diff_uncertainties
)

scaled_models = dict()
for scaler in scalers.index:
    scaled_models[scaler] = ScaledScoringModel(
        base_model=learned_models[scaler], 
        multiplicator=scaler_multiplicators[scaler][0], 
        translation=scaler_translations[scaler][0],
        multiplicator_left_uncertainty=scaler_multiplicators[scaler][1], 
        multiplicator_right_uncertainty=scaler_multiplicators[scaler][1], 
        translation_left_uncertainty=scaler_translations[scaler][1],
        translation_right_uncertainty=scaler_translations[scaler][1]
    )

nonscaler_model_norms = mehestan.compute_model_norms(learned_models, nonscalers, entities, privacy)
nonscaler_entity_ratios = mehestan.compute_entity_ratios(learned_models, scaled_models, entities,
    nonscalers, scalers, privacy)
nonscaler_ratio_voting_rights, nonscaler_ratios, nonscaler_ratio_uncertainties = _aggregate_user_comparisons(
    scalers, nonscaler_entity_ratios, 
    error=mehestan.error, 
    lipschitz=mehestan.user_comparison_lipschitz
)
nonscaler_multiplicators = mehestan.compute_multiplicators(
    nonscaler_ratio_voting_rights, nonscaler_ratios, nonscaler_ratio_uncertainties, 
    nonscaler_model_norms
)

nonscaler_entity_diffs = mehestan.compute_entity_diffs(
    learned_models, scaled_models, nonscalers, scalers, entities, privacy, nonscaler_multiplicators
)
nonscaler_diff_voting_rights, nonscaler_diffs, nonscaler_diff_uncertainties = _aggregate_user_comparisons(
    scalers, nonscaler_entity_diffs, 
    error=mehestan.error, lipschitz=mehestan.user_comparison_lipschitz
)
nonscaler_translations = mehestan.compute_translations(
    nonscaler_diff_voting_rights, nonscaler_diffs, nonscaler_diff_uncertainties
)

scaled_models |= { 
    u: ScaledScoringModel(
        base_model=learned_models[u], 
        multiplicator=nonscaler_multiplicators[u][0], 
        translation=nonscaler_translations[u][0],
        multiplicator_left_uncertainty=nonscaler_multiplicators[u][1], 
        multiplicator_right_uncertainty=nonscaler_multiplicators[u][1], 
        translation_left_uncertainty=nonscaler_translations[u][1],
        translation_right_uncertainty=nonscaler_translations[u][1]
    ) for u in nonscalers.index
}

