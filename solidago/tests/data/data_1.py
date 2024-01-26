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
from solidago.pipeline import Pipeline


users = pd.DataFrame(dict(
    is_pretrusted=[True, False, False, True, True],
    trust_score=[0.8, 0.21333333333333335, 0.028444444444444446, 0.8037925925925926, 0.8]
))
users.index.name = "user_id"

vouches = pd.DataFrame(dict(
    voucher=[0, 4, 1, 2],
    vouchee=[1, 1, 2, 3],
    vouch=[1, 1, 1, 1]
))

entities = pd.DataFrame(dict(
    cumulative_trust=[1.737007, 1.737007],
    min_voting_right=[1.0, 1.0],
    overtrust=[1.762993, 1.762993]
))
entities.index.name = "entity_id"

privacy = PrivacySettings({
    0: { 0: True,  1: True, 2: False, 3: True, 4: False },
    1: { 0: False, 1: True, 2: False, 3: True, 4: True }
})

judgments = DataFrameJudgments(pd.DataFrame(dict(
    user_id=[0, 1, 2, 3, 4],
    entity_a=[0, 0, 1, 0, 1],
    entity_b=[1, 1, 0, 1, 0],
    comparison=[-5, 3, -4, -8, -10],
    comparison_max=[10, 10, 10, 10, 10]
)))

pipeline = Pipeline(
    trust_propagation=LipschiTrust(
        pretrust_value=0.8,
        decay=0.8,
        sink_vouch=5.0,
        error=1e-8
    ),
    voting_rights=AffineOvertrust(
        privacy_penalty=0.5, 
        min_overtrust=2.0,
        overtrust_ratio=0.1,
    ),
    preference_learning=UniformGBT(
        prior_std_dev=7,
        convergence_error=1e-5,
        cumulant_generating_function_error=1e-5,
    ),
    scaling=ScalingCompose(
        Mehestan(
            lipschitz=10,
            min_activity=0.1,
            n_scalers_max=100,
            privacy_penalty=0.5,
            p_norm_for_multiplicative_resilience=4.0,
            error=1e-5
        ),
        QuantileZeroShift(
            zero_quantile=0.15,
            lipschitz=0.1,
            error=1e-5
        )
    ),
    aggregation=QuantileStandardizedQrMedian(
        dev_quantile=0.9,
        lipschitz=0.1,
        error=1e-5
    ),
    post_process=Squash(
        score_max=100
    )
)

voting_rights = VotingRights({
    0: {0: 0.5, 1: 0.5, 2: 1.0, 3: 0.5, 4: 1.0},
    1: {0: 1.0, 1: 0.5, 2: 1.0, 3: 0.5, 4: 0.5}
})

learned_models = {
    0: DirectScoringModel({
        0: (0.8543576022084396, 0.22268338112332428, 0.22268338112332428),
        1: (-0.8542675414366053, 0.22268338112332428, 0.22268338112332428)
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

mehestan_scaled_models = {
    0: ScaledScoringModel(
        base_model=learned_models[0],
        multiplicator=1,
        translation=-0.03468579367348186,
        multiplicator_left_uncertainty=1,
        multiplicator_right_uncertainty=1,
        translation_left_uncertainty=0.036163155262318135,
        translation_right_uncertainty=0.036163155262318135,
    ),
    3: ScaledScoringModel(
        base_model=learned_models[3],
        multiplicator=1,
        translation=0.017706130481562745,
        multiplicator_left_uncertainty=1,
        multiplicator_right_uncertainty=1,
        translation_left_uncertainty=0.07757147389225401,
        translation_right_uncertainty=0.07757147389225401,
    ),
    4: ScaledScoringModel(
        base_model=learned_models[4],
        multiplicator=1,
        translation=0.016677228572662375,
        multiplicator_left_uncertainty=1,
        multiplicator_right_uncertainty=1,
        translation_left_uncertainty=0.03018889076138863,
        translation_right_uncertainty=0.03018889076138863,
    ),
    1: ScaledScoringModel(
        base_model=learned_models[1],
        multiplicator=1,
        translation=-0.48392198001455006,
        multiplicator_left_uncertainty=1,
        multiplicator_right_uncertainty=1,
        translation_left_uncertainty=0.25472139651232334,
        translation_right_uncertainty=0.25472139651232334,
    ),
    2: ScaledScoringModel(
        base_model=learned_models[2],
        multiplicator=1,
        translation=-0.43024928594487194,
        multiplicator_left_uncertainty=1,
        multiplicator_right_uncertainty=1,
        translation_left_uncertainty=0.3058947623607349,
        translation_right_uncertainty=0.3058947623607349,
    ),
}

zero_shifted_models = {
    0: ScaledScoringModel(
        base_model=learned_models[0],
        multiplicator=1,
        translation=-0.03468579367348186,
        multiplicator_left_uncertainty=1,
        multiplicator_right_uncertainty=1,
        translation_left_uncertainty=0.036163155262318135,
        translation_right_uncertainty=0.036163155262318135,
    ),
    3: ScaledScoringModel(
        base_model=learned_models[3],
        multiplicator=1,
        translation=0.017706130481562745,
        multiplicator_left_uncertainty=1,
        multiplicator_right_uncertainty=1,
        translation_left_uncertainty=0.07757147389225401,
        translation_right_uncertainty=0.07757147389225401,
    ),
    4: ScaledScoringModel(
        base_model=learned_models[4],
        multiplicator=1,
        translation=0.016677228572662375,
        multiplicator_left_uncertainty=1,
        multiplicator_right_uncertainty=1,
        translation_left_uncertainty=0.03018889076138863,
        translation_right_uncertainty=0.03018889076138863,
    ),
    1: ScaledScoringModel(
        base_model=learned_models[1],
        multiplicator=1,
        translation=-0.48392198001455006,
        multiplicator_left_uncertainty=1,
        multiplicator_right_uncertainty=1,
        translation_left_uncertainty=0.25472139651232334,
        translation_right_uncertainty=0.25472139651232334,
    ),
    2: ScaledScoringModel(
        base_model=learned_models[2],
        multiplicator=1,
        translation=-0.43024928594487194,
        multiplicator_left_uncertainty=1,
        multiplicator_right_uncertainty=1,
        translation_left_uncertainty=0.3058947623607349,
        translation_right_uncertainty=0.3058947623607349,
    ),
}


standardized_models, global_model = dict(), DirectScoringModel()
displayed_models, displayed_global_model = dict(), DirectScoringModel()
