import pytest
import importlib
import pandas as pd
import numpy as np

from solidago.privacy_settings import PrivacySettings
from solidago.judgments import DataFrameJudgments
from solidago.scoring_model import DirectScoringModel, ScaledScoringModel

from solidago.trust_propagation import LipschiTrust
from solidago.voting_rights import VotingRights, AffineOvertrust
from solidago.preference_learning import UniformGBT
from solidago.scaling import ScalingCompose, Mehestan, QuantileZeroShift
from solidago.aggregation import QuantileStandardizedQrMedian
from solidago.post_process import Squash

from solidago.scaling.mehestan import (Mehestan, _compute_activities, _model_norms, 
    _compute_score_diffs, _compute_user_score_diffs, _aggregate_user_comparisons, _aggregate)


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
    trust_score=[1] * 5,
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

score_diffs = _compute_score_diffs(learned_models, users, entities)
activities = _compute_activities(score_diffs, users, privacy, mehestan.privacy_penalty)
is_scaler = mehestan.compute_scalers(activities, users)
users = users.assign(is_scaler=is_scaler)
scalers = users[users["is_scaler"]]
nonscalers = users[users["is_scaler"] == False]
        
model_norms = _model_norms(learned_models, entities, privacy, 
    power=mehestan.p_norm_for_multiplicative_resilience,
    privacy_penalty=mehestan.privacy_penalty
)
scaler_entity_ratios = mehestan.compute_entity_ratios(scalers, scalers, score_diffs)
scaler_ratio_voting_rights, scaler_ratios, scaler_ratio_uncertainties = _aggregate_user_comparisons(
    scalers, scaler_entity_ratios, 
    error=mehestan.error, lipschitz=mehestan.user_comparison_lipschitz
)
multiplicators = mehestan.compute_multiplicators(
    scaler_ratio_voting_rights, scaler_ratios, scaler_ratio_uncertainties, model_norms
)
scaler_entity_diffs = mehestan.compute_entity_diffs(
    learned_models, scalers, scalers, entities, multiplicators
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
        multiplicator=multiplicators[scaler][0], 
        translation=scaler_translations[scaler][0],
        multiplicator_left_uncertainty=multiplicators[scaler][1], 
        multiplicator_right_uncertainty=multiplicators[scaler][1], 
        translation_left_uncertainty=scaler_translations[scaler][1],
        translation_right_uncertainty=scaler_translations[scaler][1]
    )
    score_diffs[scaler] = _compute_user_score_diffs(scaled_models[scaler], entities)

scalee_entity_ratios = mehestan.compute_entity_ratios(nonscalers, scalers, score_diffs)
scalee_ratio_voting_rights, scalee_ratios, scalee_ratio_uncertainties = _aggregate_user_comparisons(
    scalers, scalee_entity_ratios, error=mehestan.error, 
    lipschitz=mehestan.user_comparison_lipschitz
)
multiplicators |= mehestan.compute_multiplicators(
    scalee_ratio_voting_rights, scalee_ratios, scalee_ratio_uncertainties, model_norms
)

scalee_entity_diffs = mehestan.compute_entity_diffs(
    learned_models, nonscalers, scalers, entities, multiplicators
)
scalee_diff_voting_rights, scalee_diffs, scalee_diff_uncertainties = _aggregate_user_comparisons(
    scalers, scalee_entity_diffs, 
    error=mehestan.error, lipschitz=mehestan.user_comparison_lipschitz
)
scalee_translations = mehestan.compute_translations(
    scalee_diff_voting_rights, scalee_diffs, scalee_diff_uncertainties
)

scaled_models |= { 
    u: ScaledScoringModel(
        base_model=learned_models[u], 
        multiplicator=multiplicators[u][0], 
        translation=scalee_translations[u][0],
        multiplicator_left_uncertainty=multiplicators[u][1], 
        multiplicator_right_uncertainty=multiplicators[u][1], 
        translation_left_uncertainty=scalee_translations[u][1],
        translation_right_uncertainty=scalee_translations[u][1]
    ) for u in nonscalers.index
}

