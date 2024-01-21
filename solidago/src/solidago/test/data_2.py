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
        initialization=dict()
    ),
    scaling=ScalingCompose(
        Mehestan(
            lipschitz=0.1,
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
    1: {0: 0.5, 8: 0.5, 2: 1.0, 4: 0.5},
    2: {0: 0.5, 2: 0.5, 4: 0.5, 6: 0.5},
    6: {0: 1.0, 8: 0.5, 2: 1.0, 6: 0.5}
})    

learned_models = {
    0: DirectScoringModel({
        1: (1.016590197621329, 0.4638561508964967, 0.4638561508964967),
        2: (-0.7877876012816142, 0.5266102124947752, 0.5266102124947752),
        6: (-0.2291324680780755, 0.5846829229672795, 0.5846829229672795)
    }),
    4: DirectScoringModel({
        1: (-0.29761600676032623, 0.33137621448368626, 0.33137621448368626),
        2: (0.2977647751812212, 0.33137621448368626, 0.33137621448368626)
    }),
    2: DirectScoringModel({
        1: (-4.965658292354929, 0.07061473411881966, 0.07061473411881966),
        2: (0.02121949850814651, 0.06043250186863176, 0.06043250186863176),
        6: (4.944447487603185, 0.030590395515494022, 0.030590395515494022)
    }),
    8: DirectScoringModel({
        1: (0.641162040422771, 0.26729930161403126, 0.26729930161403126),
        6: (-0.6412757158129634, 0.26729930161403126, 0.26729930161403126)
    }),
    6: DirectScoringModel({
        2: (0.6412670367706619, 0.26730021787214453, 0.26730021787214453),
        6: (-0.64116204042277, 0.26730021787214453, 0.26730021787214453)
    })
}

mehestan_scaled_models = dict()
zero_shifted_models = dict()

standardized_models, global_model = dict(), DirectScoringModel()
displayed_models, displayed_global_model = dict(), DirectScoringModel()
