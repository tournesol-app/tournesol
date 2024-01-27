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

from solidago.scaling import Mehestan


def test_data():
    m = Mehestan(
        lipschitz=1, 
        min_activity=1, 
        n_scalers_max=10, 
        privacy_penalty=0.5,
        p_norm_for_multiplicative_resilience=4.0,
        error=1e-5
    )
    
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
    
    user_models = {
        0: DirectScoringModel({
            0: (0, 0, 0),
            1: (1, 0, 0),
            2: (2, 0, 0),
            3: (3, 0, 0),
            4: (4, 0, 0),
        }),
        1: DirectScoringModel({
            0: (-0.45987485219302987, 0.3040980645995397, 0.3040980645995397),
            1: (0.46000589337922315, 0.3040980645995397, 0.3040980645995397)
        }),
        2: DirectScoringModel({
            0: (-0.6411620404227717, 0.26730021787214453, 0.26730021787214453),
            1: (0.6412670367706607, 0.26730021787214453, 0.26730021787214453)
        }),
        3: DirectScoringModel({
            0: (2.0611090358800523, 0.07820614406839796, 0.07820614406839796),
            1: (-2.061088795104216, 0.07820614406839796, 0.07820614406839796)
        }),
        4: DirectScoringModel({
            0: (-4.949746148097695, 0.030612236968599268, 0.030612236968599268),
            1: (4.949747745198173, 0.030612236968599268, 0.030612236968599268)
        })
    }

