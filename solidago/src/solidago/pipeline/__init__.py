from .inputs import TournesolInput
from .outputs import PipelineOutput
from .parameters import PipelineParameters

from dataclasses import dataclass
from typing import Optional

import pandas as pd
import logging

from solidago import PrivacySettings, Judgments
from solidago.scoring_model import ScoringModel, DirectScoringModel, PostProcessedScoringModel

from solidago.trust_propagation import TrustPropagation, LipschiTrust
from solidago.voting_rights import VotingRights, VotingRightsAssignment, AffineOvertrust
from solidago.preference_learning import PreferenceLearning, UniformGBT
from solidago.scaling import Scaling, ScalingCompose, Mehestan, QuantileZeroShift
from solidago.aggregation import Aggregation, QuantileStandardizedQrMedian
from solidago.post_process import PostProcess, Squash

logger = logging.getLogger(__name__)


@dataclass
class DefaultPipeline:
    """ Instantiates the default pipeline described in
    "Solidago: A Modular Pipeline for Collaborative Scaling".
    """
    trust_propagation: TrustPropagation = LipschiTrust(
        pretrust_value=0.8,
        decay=0.8,
        sink_vouch=5.0,
        error=1e-8
    )
    voting_rights: VotingRights = AffineOvertrust(
        privacy_penalty=0.5, 
        min_overtrust=2.0,
        overtrust_ratio=0.1,
    )
    preference_learning: PreferenceLearning = UniformGBT(
        prior_std_dev=7,
        convergence_error=1e-5,
        cumulant_generating_function_error=1e-5,
        initialization=dict()
    )
    scaling: Scaling = ScalingCompose(
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
    )
    aggregation: Aggregation = QuantileStandardizedQrMedian(
        dev_quantile=0.9,
        lipschitz=0.1,
        error=1e-5
    )
    post_process: PostProcess = Squash(
        score_max=100
    )


class Pipeline:
    def __init__(
        self,
        trust_propagation: TrustPropagation = DefaultPipeline.trust_propagation,
        voting_rights: VotingRights = DefaultPipeline.voting_rights,
        preference_learning: PreferenceLearning = DefaultPipeline.preference_learning,
        scaling: Scaling = DefaultPipeline.scaling,
        aggregation: Aggregation = DefaultPipeline.aggregation,
        post_process: PostProcess = DefaultPipeline.post_process
    ):
        """ Instantiates the pipeline components.
        
        Parameters
        ----------
        trust_propagation: TrustPropagation
            Algorithm to spread trust based on pretrusts and vouches
        voting_rights: VotingRights
            Algorithm to assign voting rights to each user
        preference_learning: PreferenceLearning
            Algorithm to learn a user model based on each user's data
        scaling: Scaling
            Algorithm to put user models on a common scale
        aggregation: Aggregation
            Algorithm to aggregate the different users' models
        post_process: PostProcess
            Algorithm to post-process user and global models,
            and make it readily usable for applications.
        """
        self.trust_propagation = trust_propagation
        self.voting_rights = voting_rights
        self.preference_learning = preference_learning
        self.scaling = scaling
        self.aggregation = aggregation
        self.post_process = post_process
        
    def __call__(
        self,
        users: pd.DataFrame,
        vouches: pd.DataFrame,
        entities: pd.DataFrame,
        privacy: PrivacySettings,
        judgments: Judgments,
        init_user_models : Optional[dict[int, ScoringModel]] = None,
        global_model: Optional[dict[int, ScoringModel]] = None,
        skip_steps: Optional[set[int]] = None
    ) -> tuple[pd.DataFrame, VotingRights, dict[int, ScoringModel], ScoringModel]:
        """ Run Pipeline 
        
        Parameters
        ----------
        users: DataFrame with columns
            * user_id: int (index)
            * is_pretrusted: bool
        vouches: DataFrame with columns
            * voucher (int)
            * vouchee (int)
            * vouch (float)
        entities: DataFrame with columns
            * entity_id: int (index)
        privacy: PrivacySettings
            privacy[user, entity] in { True, False, None }
        judgments: Jugdments
            judgments[user] must yield the judgment data provided by the user
        user_models: dict[int, UserModel]
            user_models[user] is the user's model
        global_model: GlobalModel
            global model
        skip_set: set[int]
            Steps that are skipped in the pipeline
            
        Returns
        -------
        trusts: DataFrame with columns
            * user_id: int (index)
            * is_pretrusted: bool
            * trust_score: float
        voting_rights: VotingRights
            voting_rights[user, entity] is the user's voting right for entity
        user_models: dict[int, UserModel]
            user_models[user] is the user's model
        global_model: GlobalModel
            global model
        """   
        if skip_steps is None:
            skip_steps = set()
        if 3 in skip_steps:
            assert init_user_models is not None
        if 5 in skip_steps:
            assert global_model is not None
            
        if len(skip_steps) == 0:
            logger.info("Starting the full Solidago pipeline")
        else:
            logger.info(
                "Starting the Solidago pipeline, skipping " 
                + ", ".join([f"Step {step}" for step in skip_steps])
            )
        
        if 1 not in skip_steps:
            logger.info(f"Pipeline 1. Propagating trust with {self.trust_propagation}")
            users = self.trust_propagation(users, vouches)
        else:
            logger.info(f"Pipeline 1. Trust propagation is skipped")
            
        if 2 not in skip_steps:
            logger.info(f"Pipeline 2. Computing voting rights with {self.voting_rights}")
            voting_rights, entities = self.voting_rights(users, entities, vouches, privacy)
        else:
            logger.info(f"Pipeline 2. Voting rights assignment is skipped")
            
        if 3 not in skip_steps:
            logger.info(f"Pipeline 3. Learning preference models with {self.preference_learning}")
            init_user_models = dict() if init_user_models is None else init_user_models
            for user, _ in users.iterrows():
                init_model = init_user_models[user] if user in init_user_models else None
                user_models[user] = self.preference_learning(judgments[user], entities, init_model)
        else:
            logger.info(f"Pipeline 3. Learning preference models is skipped")
            user_models = {
                init_user_models[user] if user in init_user_models else DirectScoringModel()
                for user, _ in users.iterrows()
            }
        
        if 4 not in skip_steps:
            logger.info(f"Pipeline 4. Collaborative scaling with {self.scaling}")
            user_models = self.scaling(user_models, users, entities, voting_rights, privacy)
        else:
            logger.info(f"Pipeline 4. Reusing precomputed scales")
            for user in user_models:
                user_models[user] = ScaledScoringModel(user_models[user], 
                    *init_user_models[user].get_scaling_parameters())
                
        if 5 not in skip_steps:
            logger.info(f"Pipeline 5. Score aggregation with {self.aggregation}")
            user_models, global_model = self.aggregation(voting_rights, user_models, users, entities)
        else:
            logger.info(f"Pipeline 5. Score aggregation skipped")
            if 6 not in skip_steps and isinstance(global_model, PostProcessedScoringModel):
                global_model = global_model.base_model
            
        if 6 not in skip_steps:
            logger.info(f"Pipeline 6. Post-processing scores {self.post_process}")
            user_models, global_model = self.post_process(user_models, global_model, entities)
        else:
            logger.info(f"Pipeline 6. Post-processing scores skipped")
        
        return users, voting_rights, user_models, global_model
        
