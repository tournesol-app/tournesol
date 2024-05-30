import pandas as pd
import numpy as np

from solidago.privacy_settings import PrivacySettings
from solidago.judgments import DataFrameJudgments
from solidago.scoring_model import DirectScoringModel, ScaledScoringModel

from solidago.trust_propagation import LipschiTrust
from solidago.voting_rights import VotingRights, AffineOvertrust
from solidago.preference_learning import UniformGBT
from solidago.scaling import ScalingCompose, Mehestan, QuantileZeroShift
from solidago.aggregation import StandardizedQrMedian
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
    aggregation=StandardizedQrMedian(
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
        0: (0.8543576022084396, 2.62, 4.52),
        1: (-0.8542675414366053, 4.55, 2.62)
    }),
    1: DirectScoringModel({
        0: (-0.45987485219302987, 3.39, 2.50),
        1: (0.46000589337922315, 2.50, 3.39)
    }),
    2: DirectScoringModel({
        0: (-0.6411620404227717, 3.84, 2.53),
        1: (0.6412670367706607, 2.53, 3.84),
    }),
    3: DirectScoringModel({
        0: (2.0611090358800523, 3.73, 11.73),
        1: (-2.061088795104216, 11.73, 3.73),
    }),
    4: DirectScoringModel({
        0: (-4.949746148097695, 1000.0, 6.26),
        1: (4.949747745198173, 6.26, 1000.0),
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

standardized_models = {
    0: DirectScoringModel({
        0: (0.5761465830553983, 0.6259462460636775, 0.9389941459706914),
        1: (-0.6248445062845347, 0.9389308423345052, 0.6258829424274912)
    }),
    3: DirectScoringModel({
        0: (1.4611973260904263, 1.5032766225727046, 1.6132186803811355),
        1: (-1.436291852224618, 1.6132044531578553, 1.5032623953494244)
    }),
    4: DirectScoringModel({
        0: (-3.467449743136944, 3.543426524728311, 3.500391896611323),
        1: (3.490895683912044, 3.5003930192118244, 3.543427647328812)
    }),
    1: DirectScoringModel({
        0: (-0.6633939514728542, 0.9297895824714835, 0.5022890657806929),
        1: (-0.016810595962338526, 0.5023811745135768, 0.9298816912043675)
    }),
    2: DirectScoringModel({
        0: (-0.7530940655832543, 1.0414555512929782, 0.6656853818827133),
        1: (0.1483241888233473, 0.6657591837219856, 1.0415293531322505)
    })
}

global_model = DirectScoringModel({
    0: (-0.10350513794452627, 0.9826512500335018, 0.9826512500335018),
    1: (-0.03791353870514101, 0.9072283664446072, 0.9072283664446072),
})

display_models, display_global_model = pipeline.post_process(
    standardized_models, global_model, entities)
