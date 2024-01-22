import logging
import numpy as np
import pandas as pd

from solidago.privacy_settings import PrivacySettings
from solidago.judgments import Judgments, DataFrameJudgments
from solidago.scoring_model import (
    ScoringModel, DirectScoringModel, ScaledScoringModel, PostProcessedScoringModel
)

from solidago.generative_model import GenerativeModel
from solidago.generative_model.user_model import UserModel, NormalUserModel
from solidago.generative_model.vouch_model import VouchModel, ErdosRenyiVouchModel
from solidago.generative_model.entity_model import EntityModel, NormalEntityModel
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



class Experiments:
    def __init__(self, n_users: int, n_entities: int):
        self.n_users = n_users
        self.n_entities = n_entities
        self.generative_model = GenerativeModel(
            user_model=NormalUserModel(
                p_trustworthy= 0.8,
                p_pretrusted= 0.2,
                zipf_vouch= 2.0,
                zipf_compare= 1.5,
                poisson_compare= 30.0,
                n_comparisons_per_entity=3.0,
                svd_dimension=5,
            ),
            vouch_model=ErdosRenyiVouchModel(),
            entity_model=NormalEntityModel(
                svd_dimension=5,
            ),
            engagement_model=SimpleEngagementModel(
                p_per_criterion={"0": 1.0}, 
                p_private=0.2
            ),
            comparison_model=KnaryGBT(n_options=21, comparison_max=10)
        )        
        self.pipeline = Pipeline(
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
        
    def sample_correlation(self, seed=0):
        data = self.generative_model(self.n_users, self.n_entities, seed)
        init_users, vouches, entities, privacy, judgments = data
        users, voting_rights, user_models, global_model = self.pipeline(*data)
        
        svd_dim, svd_cols = 0, list()
        while f"svd{svd_dim}" in entities:
            svd_cols.append(f"svd{svd_dim}")
            svd_dim += 1
        
        truth = entities[svd_cols].sum(axis=1)
        estimate = [global_model(e, row)[0] for e, row in entities.iterrows()]
        return np.corrcoef(truth, estimate)[0, 1]
    
    def sample_n_correlations(self, n_seeds=5):
        return list(self.sample_correlation(seed) for seed in range(n_seeds))

    def setattr(self, x_parameter: str, x: float):
        obj = self
        x_list = x_parameter.split(".")
        for attr in x_list[:-1]:
            try:
                obj = getattr(obj, attr)
            except:
                obj = obj[attr]
        try:
            setattr(obj, x_list[-1], x)
        except:
            obj[x_parameter[-1]] = x
    
    def getattr(self, x_parameter: str):
        obj = self
        for attr in x_parameter.split("."):
            try:
                obj = getattr(obj, attr)
            except:
                obj = obj[attr]
        return obj
        
    def run_experiments(
        self,
        n_seeds: int, 
        x_parameter: str, 
        x_values: list[float], 
        z_parameter: str, 
        z_values: list[float]
    ):
        """ Run experiments with multiple seeds. Outputs results in json.
        
        Parameters
        ----------
        n_users: int
        n_entities: int
        n_seeds: int
            For reproducibility and variance estimation.
        x_parameter: str
            path towards parameter, e.g. "generative_model.user_model.p_trustworthy"
        x_values: list[float]
            list of changed values for this attribute
        z_parameter: tuple[str]
            path towards parameter, e.g. "pipeline.aggregation.lipschitz"
        z_values: list[float]
            list of changed values for this attribute        
        
        Returns
        -------
        json: dict[str, list[list[list[float]]]]
            json["generative_model"] describes the base generative model
            json["pipeline"] describes the base pipeline
            json["results"][z_value][x_value][seed] is the score of the output.
        """
        results = list()
        base_x = self.getattr(x_parameter)
        base_z = self.getattr(z_parameter)
        
        for z in z_values:
            z_results = list()
            self.setattr(z_parameter, z)
            for x in x_values:
                self.setattr(x_parameter, x)
                z_results.append(self.sample_n_correlations(n_seeds))
            results.append(z_results)
        
        self.setattr(x_parameter, base_x)
        self.setattr(z_parameter, base_z)        
        return { 
            "n_users": self.n_users,
            "n_entities": self.n_entities,
            "generative_model": self.generative_model.to_json(), 
            "pipeline": self.pipeline.to_json(), 
            "x_parameter": x_parameter,
            "x_values": x_values,
            "z_parameter": z_parameter,
            "z_values": z_values,
            "results": results 
        }
    
