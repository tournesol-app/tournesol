import logging
import numpy as np
import pandas as pd

from solidago.privacy_settings import PrivacySettings
from solidago.judgments import Judgments, DataFrameJudgments
from solidago.scoring_model import (
    ScoringModel, DirectScoringModel, ScaledScoringModel, PostProcessedScoringModel
)

from solidago.generative_model import GenerativeModel
from solidago.generative_model.user_model import UserModel, SvdUserModel
from solidago.generative_model.vouch_model import VouchModel, ErdosRenyiVouchModel
from solidago.generative_model.entity_model import EntityModel, SvdEntityModel
from solidago.generative_model.engagement_model import EngagementModel, SimpleEngagementModel
from solidago.generative_model.comparison_model import ComparisonModel, KnaryGBT

from solidago.pipeline import Pipeline
from solidago.trust_propagation import TrustPropagation, LipschiTrust
from solidago.voting_rights import VotingRights, VotingRightsAssignment, AffineOvertrust
from solidago.preference_learning import PreferenceLearning, UniformGBT
from solidago.scaling import Scaling, ScalingCompose, Mehestan, QuantileZeroShift
from solidago.aggregation import Aggregation, QuantileStandardizedQrMedian
from solidago.post_process import PostProcess, Squash

logger = logging.getLogger(__name__)


generative_model = GenerativeModel(
    user_model=SvdUserModel(
        p_trustworthy= 0.8,
        p_pretrusted= 0.2,
        zipf_vouch= 2.0,
        zipf_compare= 1.5,
        poisson_compare= 30.0,
        n_comparisons_per_entity=3.0,
        svd_dimension=5,
        svd_distribution=lambda svd_dim: np.random.normal(1, 1, svd_dim)
    ),
    vouch_model=ErdosRenyiVouchModel(),
    entity_model=SvdEntityModel(
        svd_dimension=5,
        svd_distribution=lambda svd_dim: np.random.normal(1, 1, svd_dim)
    ),
    engagement_model=SimpleEngagementModel(
        p_per_criterion={"0": 1.0}, 
        p_private=0.2
    ),
    comparison_model=KnaryGBT(n_options=21, comparison_max=10)
)

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
            lipschitz=1,
            min_activity=1,
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


def correlation(x, y):
    xmean = x.mean()
    ymean = y.mean()
    return (x-xmean) @ (y-ymean) / np.linalg.norm(x - xmean) / np.linalg.norm(y - ymean)
    
def score(entities, global_model):
    svd_dim, svd_cols = 0, list()
    while f"svd{svd_dim}" in entities:
        svd_cols.append(f"svd{svd_dim}")
        svd_dim += 1
    truth = entities[svd_cols].sum(axis=1)
    estimate = np.array([global_model(e, None)[0] for e in entities.index])
    return correlation(truth, estimate)
 
def sample_score(n_users=50, n_entities=20, seed=0):
     data = generative_model(n_users, n_entities, seed)
     init_users, vouches, entities, privacy, judgments = data
     users, voting_rights, user_models, global_model = pipeline(*data)
     return score(entities, global_model)

def sample_n_scores(n_users=50, n_entities=20, n_seeds=5):
    return list(sample_score(n_users, n_entities, seed) for seed in range(n_seeds))
     
def vary_p_trustworthy(n_users=50, n_entities=20, n_seeds=5, ps=[0, .2, .5, .5, 1]):
    results = list()
    for p in ps:
        generative_model.user_model.p_trustworthy = p
        results.append(sample_n_scores(n_users, n_entities, n_seeds))
    return ps, results
    

