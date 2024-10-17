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
    trust_score=[0.8, 0.2171945701357466, 0.0, 0.8289592760180996, 0.8]
), index=[0, 4, 2, 8, 6])
users.index.name = "user_id"

vouches = pd.DataFrame(dict(
    voucher=[0, 4, 8, 2],
    vouchee=[4, 8, 4, 4],
    vouch=[1, 1, 1, 1]
))

entities = pd.DataFrame(dict(
    cumulative_trust=[0.9230769230769231, 1.6144796380090498, 0.9085972850678733],
    min_voting_right=[1.0, 1.0, 1.0],
    overtrust=[1.5769230769230769, 1.3855203619909502, 1.0914027149321268]
), index=[1, 6, 2])
entities.index.name = "entity_id"

privacy = PrivacySettings({ 
    1: { 0: True,  4: True, 2: False, 8: True },
    6: { 0: False, 2: False, 8: True, 6: True },
    2: { 0: True, 4: True, 2: True, 6: True }
})

judgments = DataFrameJudgments(pd.DataFrame(dict(
    user_id=[0, 0, 0, 2, 2, 4, 6, 8],
    entity_a=[1, 2, 1, 2, 6, 1, 6, 1],
    entity_b=[6, 6, 2, 1, 1, 2, 2, 6],
    comparison=[-5, 3, -4, -8, -10, 2, 4, -4],
    comparison_max=[10, 10, 10, 10, 10, 10, 10, 10]
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
            lipschitz=100,
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
    1: {0: 0.5, 8: 0.5, 2: 1.0, 4: 0.5},
    2: {0: 0.5, 2: 0.5, 4: 0.5, 6: 0.5},
    6: {0: 1.0, 8: 0.5, 2: 1.0, 6: 0.5}
})    

learned_models = {
    0: DirectScoringModel(
        {
            1: (1.0166024998812924, 1.86, 2.67),
            2: (-0.7877792323989169, 2.36, 1.84),
            6: (-0.22912573047151286, 2.0, 1.89),
        }
    ),
    4: DirectScoringModel(
        {
            1: (-0.29762516882114326, 3.07, 2.52),
            2: (0.297764775194798, 2.52, 3.07),
        }
    ),
    2: DirectScoringModel(
        {
            1: (-4.965657348164456, 17.7, 3.7),
            2: (0.021224904768728296, 4.57, 10.74),
            6: (4.944450204676572, 6.27, 1000.0),
        }
    ),
    8: DirectScoringModel(
        {
            1: (0.6412670367706624, 2.53, 3.84),
            6: (-0.6411620404227696, 3.84, 2.53),
        }
    ),
    6: DirectScoringModel(
        {
            2: (0.6411620404227699, 2.53, 3.84),
            6: (-0.6412757158129653, 3.84, 2.53),
        }
    ),
}

mehestan_scaled_models = {
    8: ScaledScoringModel(
        base_model=learned_models[8],
        multiplicator=1,
        translation=0.0003394454649724929,
        multiplicator_left_uncertainty=1,
        multiplicator_right_uncertainty=1,
        translation_left_uncertainty=0.00030018716707924653,
        translation_right_uncertainty=0.00030018716707924653,
    ),
    6: ScaledScoringModel(
        base_model=learned_models[6],
        multiplicator=1,
        translation=-0.00034074628445921883,
        multiplicator_left_uncertainty=1,
        multiplicator_right_uncertainty=1,
        translation_left_uncertainty=0.0806569007844027,
        translation_right_uncertainty=0.0806569007844027,
    ),
    0: ScaledScoringModel(
        base_model=learned_models[0],
        multiplicator=1,
        translation=-1.403453157169231,
        multiplicator_left_uncertainty=1,
        multiplicator_right_uncertainty=1,
        translation_left_uncertainty=1.2672222659229513,
        translation_right_uncertainty=1.2672222659229513,
    ),
    4: ScaledScoringModel(
        base_model=learned_models[4],
        multiplicator=1,
        translation=0.8223586007875764,
        multiplicator_left_uncertainty=1,
        multiplicator_right_uncertainty=1,
        translation_left_uncertainty=0.5562825105148258,
        translation_right_uncertainty=0.5562825105148258,
    ),
    2: ScaledScoringModel(
        base_model=learned_models[2],
        multiplicator=1,
        translation=-0.8915505524653426,
        multiplicator_left_uncertainty=1,
        multiplicator_right_uncertainty=1,
        translation_left_uncertainty=0.8165439585017585,
        translation_right_uncertainty=0.8165439585017585,
    ),
}

zero_shifted_models = {
    8: ScaledScoringModel(
        base_model=learned_models[8],
        multiplicator=1,
        translation=0.0003394454649724929,
        multiplicator_left_uncertainty=1,
        multiplicator_right_uncertainty=1,
        translation_left_uncertainty=0.00030018716707924653,
        translation_right_uncertainty=0.00030018716707924653,
    ),
    6: ScaledScoringModel(
        base_model=learned_models[6],
        multiplicator=1,
        translation=-0.00034074628445921883,
        multiplicator_left_uncertainty=1,
        multiplicator_right_uncertainty=1,
        translation_left_uncertainty=0.0806569007844027,
        translation_right_uncertainty=0.0806569007844027,
    ),
    0: ScaledScoringModel(
        base_model=learned_models[0],
        multiplicator=1,
        translation=-1.403453157169231,
        multiplicator_left_uncertainty=1,
        multiplicator_right_uncertainty=1,
        translation_left_uncertainty=1.2672222659229513,
        translation_right_uncertainty=1.2672222659229513,
    ),
    4: ScaledScoringModel(
        base_model=learned_models[4],
        multiplicator=1,
        translation=0.8223586007875764,
        multiplicator_left_uncertainty=1,
        multiplicator_right_uncertainty=1,
        translation_left_uncertainty=0.5562825105148258,
        translation_right_uncertainty=0.5562825105148258,
    ),
    2: ScaledScoringModel(
        base_model=learned_models[2],
        multiplicator=1,
        translation=-0.8915505524653426,
        multiplicator_left_uncertainty=1,
        multiplicator_right_uncertainty=1,
        translation_left_uncertainty=0.8165439585017585,
        translation_right_uncertainty=0.8165439585017585,
    ),
}


standardized_models = {
    8: DirectScoringModel({
        1: (0.4356690948334647, 0.43564243296675964, 0.7987095414478789),
        6: (-0.4352852345494171, 0.798786742912629, 0.4357196344315098)
    }),
    6: DirectScoringModel({
        2: (0.43527845682957156, 0.4902871705401842, 0.8533555235557329),
        6: (-0.43566997827155546, 0.8532842163727361, 0.49021586335718753)
    }),
    0: DirectScoringModel({
        1: (-0.2627339750859491, 1.5510275979872548, 2.1810738062648616),
        2: (-1.4881584825565468, 2.110922433889936, 1.395638682706841),
        6: (-1.1087536307189239, 1.8103965426242272, 1.4991706541092893)
    }),
    4: DirectScoringModel({
        1: (0.35637350183850014, 1.0300177933546122, 0.625772131807037),
        2: (0.760720197919427, 0.6256710972736853, 1.0301188278879638)
    }),
    2: DirectScoringModel({
        1: (-3.9778627669772106, 4.0228373466577585, 3.926922814977825),
        2: (-0.5910763276849823, 0.6222205920649049, 0.6510425976603276),
        6: (2.752483007488795, 3.912517716454797, 3.954068017484545)
    })
}

global_model = DirectScoringModel({
    1: (-0.022891233656453326, 0.9532143443921428, 0.9532143443921428),
    2: (0.0015751422556766616, 0.9562056836168252, 0.9562056836168252),
    6: (-0.061725183936710955, 0.9764219077260424, 0.9764219077260424),
})

display_models, display_global_model = pipeline.post_process(
    standardized_models, global_model, entities)
