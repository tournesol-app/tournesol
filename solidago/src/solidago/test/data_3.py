import pandas as pd
import numpy as np

from solidago.privacy_settings import PrivacySettings
from solidago.judgments import DataFrameJudgments
from solidago.scoring_model import DirectScoringModel

from solidago.trust_propagation import LipschiTrust
from solidago.voting_rights import VotingRights, AffineOvertrust
from solidago.preference_learning import UniformGBT
from solidago.scaling import ScalingCompose, Mehestan, QuantileZeroShift
from solidago.aggregation import QuantileStandardizedQrMedian
from solidago.post_process import Squash
from solidago.pipeline import Pipeline


users = pd.DataFrame(dict(
    is_pretrusted=(np.arange(5) % 3 == 0),
    trust_score=[0.8, 0.0, 0.0, 0.8, 0.21333333333333335],
    svd0=[1, 2, 5, 2, 1],
    svd1=[7, 2, 0, 1, 9]
))
users.index.name = "user_id"

vouches = pd.DataFrame(dict(
    voucher=[0, 1, 2, 3],
    vouchee=[4, 4, 4, 4],
    vouch=[1, 1, 1, 1]
))

entities = pd.DataFrame(dict(
    cumulative_trust=[1.0133333333333334,
        0.6133333333333334,
        1.4133333333333336,
        1.0133333333333334,
        0.8
    ],
    min_voting_right=[0.8899044990539551, 0.8915553092956543, 1.0, 1.0, 1.0],
    overtrust=[2.101332413355509,
        2.0613325945536296,
        1.5866666666666664,
        1.4866666666666666,
        1.2
    ],
    svd0=[-1, 2, -1, 0, 0],
    svd1=[0, 0, 6, 4, 2]
))
entities.index.name = "entity_id"

privacy = PrivacySettings({
    0: { 0: True,  1: True, 2: False, 3: True, 4: False },
    1: { 1: True, 2: False, 3: True, 4: False },
    2: { 0: False,  1: True, 3: True, 4: False },
    3: { 0: True,  1: True, 3: True, 4: False },
    4: { 0: True,  1: True, 2: True, 3: True }
})

judgments = DataFrameJudgments(pd.DataFrame(dict(
    user_id= [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 3, 3, 3, 3, 3, 3, 4, 4, 4],
    entity_a=[0, 2, 4, 0, 1, 4, 3, 4, 0, 2, 1, 0, 4, 0, 0, 0, 0, 2, 4, 0, 1, 2],
    entity_b=[2, 3, 3, 2, 2, 3, 2, 1, 4, 3, 0, 4, 1, 1, 2, 3, 4, 3, 3, 1, 2, 3],
    comparison=    [-5,3,-4,-3,-3, 2, 4,-4, 3, 2, 1, 3, 4, 1, 2, 1, 2, 0,-1, 2,-1,-2],
    comparison_max=[5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5]
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
        initialization=dict()
    ),
    scaling=ScalingCompose(
        Mehestan(
            lipschitz=0.1,
            min_activity=10,
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
    0: {
        0: 0.44495224952697754,
        1: 0.44495224952697754,
        2: 0.8899044990539551,
        3: 0.44495224952697754,
        4: 0.8899044990539551
    },
    1: {
        1: 0.44577765464782715,
        2: 0.8915553092956543,
        3: 0.44577765464782715,
        4: 0.8915553092956543
    },
    2: {0: 1.0, 1: 0.5, 3: 0.5, 4: 1.0},
    3: {0: 0.5, 1: 0.5, 3: 0.5, 4: 1.0},
    4: {0: 0.5, 1: 0.5, 2: 0.5, 3: 0.5}
})

preference_learned_models = {
    0: DirectScoringModel({
        0: (5.033398104293532, 0.03096002542681708, 0.03096002542681708),
        2: (-4.70158398961812, 0.16736063832963174, 0.16736063832963174),
        3: (-2.2520973379065916, 0.21329795423450776, 0.21329795423450776),
        4: (1.920367641692402, 0.07689734133169311, 0.07689734133169311)
    }),
    1: DirectScoringModel({
        0: (-0.2647961020419981, 0.4346751126408668, 0.4346751126408668),
        1: (-0.723484071079214, 0.4387030807322584, 0.4387030807322584),
        2: (-1.9388463288575928, 0.5587891835427051, 0.5587891835427051),
        3: (1.5444643844051669, 0.4306522267140735, 0.4306522267140735),
        4: (1.383154679686365, 0.7248330732791874, 0.7248330732791874)
    }),
    2: DirectScoringModel({
        0: (-0.41403365335425246, 0.6232992917299677, 0.6232992917299677),
        1: (0.6217382466724807, 0.5848617488561728, 0.5848617488561728),
        4: (-0.2073399097731925, 0.6429793786107434, 0.6429793786107434)
    }),
    3: DirectScoringModel({
        0: (-0.7616735994053457, 1.136102459884623, 1.136102459884623),
        1: (-0.1376152832458718, 0.32929993602267005, 0.32929993602267005),
        2: (0.26367367798854036, 0.6238313087499935, 0.6238313087499935),
        3: (0.03904465536134892, 0.958527480363601, 0.958527480363601),
        4: (0.5972697855709417, 0.5727475480020277, 0.5727475480020277)
    }),
    4: DirectScoringModel({
        0: (-0.374212225919361, 0.2649557275176049, 0.2649557275176049),
        1: (0.9304055634303148, 0.5771139502767695, 0.5771139502767695),
        2: (0.351959458123829, 0.5817762983596343, 0.5817762983596343),
        3: (-0.9084921677179439, 0.2696180756004697, 0.2696180756004697)
    })
}

mehestan_scaled_models = dict()
zero_shifted_models = dict()

standardized_models, global_model = dict(), DirectScoringModel()
displayed_models, displayed_global_model = dict(), DirectScoringModel()
