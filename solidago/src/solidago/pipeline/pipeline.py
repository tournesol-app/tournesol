from dataclasses import dataclass
from typing import Mapping, Optional

import numpy as np
import pandas as pd
import logging
import timeit

from solidago import PrivacySettings, Judgments
from solidago.scoring_model import ScoringModel, ScaledScoringModel

from solidago.trust_propagation import TrustPropagation, TrustAll, LipschiTrust, NoTrustPropagation
from solidago.preference_learning import PreferenceLearning, UniformGBT
from solidago.voting_rights import VotingRights, VotingRightsAssignment, AffineOvertrust, IsTrust
from solidago.scaling import Scaling, ScalingCompose, Mehestan, QuantileZeroShift, Standardize, NoScaling
from solidago.aggregation import Aggregation, StandardizedQrMedian, StandardizedQrQuantile, Average, EntitywiseQrQuantile
from solidago.post_process import PostProcess, Squash, NoPostProcess

from solidago.pipeline.inputs import PipelineInput
from solidago.pipeline.outputs import PipelineOutput

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
    preference_learning: PreferenceLearning = UniformGBT(
        prior_std_dev=7,
        convergence_error=1e-5,
        cumulant_generating_function_error=1e-5,
    )
    voting_rights: VotingRightsAssignment = AffineOvertrust(
        privacy_penalty=0.5, 
        min_overtrust=2.0,
        overtrust_ratio=0.1,
    )
    scaling: Scaling = ScalingCompose(
        Mehestan(
            lipschitz=0.1,
            min_activity=10.0,
            n_scalers_max=100,
            privacy_penalty=0.5,
            p_norm_for_multiplicative_resilience=4.0,
            error=1e-5
        ),
        QuantileZeroShift(
            zero_quantile=0.15,
            lipschitz=0.1,
            error=1e-5
        ),
        Standardize(
            dev_quantile=0.9,
            lipschitz=0.1,
            error=1e-5
        )
    )
    aggregation: Aggregation = EntitywiseQrQuantile(
        quantile=0.2,
        lipschitz=0.1,
        error=1e-5
    )
    post_process: PostProcess = Squash(
        score_max=100
    )


class Pipeline:
    def __init__(
        self,
        *,
        trust_propagation: TrustPropagation = DefaultPipeline.trust_propagation,
        preference_learning: PreferenceLearning = DefaultPipeline.preference_learning,
        voting_rights: VotingRightsAssignment = DefaultPipeline.voting_rights,
        scaling: Scaling = DefaultPipeline.scaling,
        aggregation: Aggregation = DefaultPipeline.aggregation,
        post_process: PostProcess = DefaultPipeline.post_process,
    ):
        """Instantiates the pipeline components.
        
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
        self.preference_learning = preference_learning
        self.voting_rights = voting_rights
        self.scaling = scaling
        self.aggregation = aggregation
        self.post_process = post_process


    @classmethod
    def from_json(cls, json) -> "Pipeline":
        return Pipeline(
            trust_propagation=trust_propagation_from_json(json["trust_propagation"]),
            preference_learning=preference_learning_from_json(json["preference_learning"]),
            voting_rights=voting_rights_from_json(json["voting_rights"]),
            scaling=scaling_from_json(json["scaling"]),
            aggregation=aggregation_from_json(json["aggregation"]),
            post_process=post_process_from_json(json["post_process"]),
        )

    def run(
        self,
        input: PipelineInput,
        criterion: str,
        output: Optional[PipelineOutput] = None
    ):
        # TODO: `criterion` should be managed by PipelineInput ?
        return self(
            **input.get_pipeline_kwargs(criterion),
            output=output,
        )

    def __call__(
        self,
        users: pd.DataFrame,
        vouches: pd.DataFrame,
        entities: pd.DataFrame,
        privacy: PrivacySettings,
        judgments: Judgments,
        init_user_models : Optional[dict[int, ScoringModel]] = None,
        output: Optional[PipelineOutput] = None,
    ) -> tuple[pd.DataFrame, VotingRights, Mapping[int, ScoringModel], ScoringModel]:
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
        init_user_models: dict[int, ScoringModel]
            user_models[user] is the user's model
            
        Returns
        -------
        users: DataFrame with columns
            * user_id: int (index)
            * is_pretrusted: bool
            * trust_score: float
        voting_rights: VotingRights
            voting_rights[user, entity] is the user's voting right for entity
        user_models: dict[int, ScoringModel]
            user_models[user] is the user's model
        global_model: ScoringModel
            global model
        """   
            
        logger.info("Starting the full Solidago pipeline")
        start_step1 = timeit.default_timer()
    
        logger.info(f"Pipeline 1. Propagating trust with {str(self.trust_propagation)}")
        users = self.trust_propagation(users, vouches)
        start_step2 = timeit.default_timer()
        logger.info(f"Pipeline 1. Terminated in {np.round(start_step2 - start_step1, 2)} seconds")
        if output is not None:
            output.save_trust_scores(trusts=users)
        
        logger.info(f"Pipeline 2. Learning preferences with {str(self.preference_learning)}")
        user_models = self.preference_learning(judgments, users, entities, init_user_models)
        start_step3 = timeit.default_timer()
        logger.info(f"Pipeline 2. Terminated in {np.round(start_step3 - start_step2, 2)} seconds")
        raw_scorings = user_models
            
        logger.info(f"Pipeline 3. Computing voting rights with {str(self.voting_rights)}")
        voting_rights, entities = self.voting_rights(users, entities, vouches, privacy, user_models)
        start_step4 = timeit.default_timer()
        logger.info(f"Pipeline 3. Terminated in {np.round(start_step4 - start_step3, 2)} seconds")
        
        logger.info(f"Pipeline 4. Collaborative scaling with {str(self.scaling)}")
        user_models = self.scaling(user_models, users, entities, voting_rights, privacy)
        start_step5 = timeit.default_timer()
        logger.info(f"Pipeline 4. Terminated in {int(start_step5 - start_step4)} seconds")
        if output is not None:
            self.save_individual_scalings(user_models, output)
                
        logger.info(f"Pipeline 5. Score aggregation with {str(self.aggregation)}")
        user_models, global_model = self.aggregation(voting_rights, user_models, users, entities)
        start_step6 = timeit.default_timer()
        logger.info(f"Pipeline 5. Terminated in {int(start_step6 - start_step5)} seconds")

        logger.info(f"Pipeline 6. Post-processing scores {str(self.post_process)}")
        user_models, global_model = self.post_process(user_models, global_model, entities)
        end = timeit.default_timer()
        logger.info(f"Pipeline 6. Terminated in {np.round(end - start_step6, 2)} seconds")
        if output is not None:
            self.save_individual_scores(user_models, raw_scorings, voting_rights, output)
            output.save_entity_scores(pd.DataFrame(
                data=[
                    dict(
                        entity_id=entity_id,
                        score=score,
                        uncertainty=left_unc+right_unc
                    )
                    for (entity_id, (score, left_unc, right_unc)) in global_model.iter_entities()
                ]
            ))
        logger.info(f"Successful pipeline run, in {int(end - start_step1)} seconds")
        return users, voting_rights, user_models, global_model
        
    def to_json(self):
        return dict(
            trust_propagation=self.trust_propagation.to_json(),
            voting_rights=self.voting_rights.to_json(),
            preference_learning=self.preference_learning.to_json(),
            scaling=self.scaling.to_json(),
            aggregation=self.aggregation.to_json(),
            post_process=self.post_process.to_json()
        )
        
    @staticmethod
    def save_individual_scalings(
        user_models: dict[int, ScaledScoringModel],
        output: PipelineOutput,
    ):
        scalings_df = pd.DataFrame(
            index=np.array(user_models.keys()),
            data={
                "s": map(lambda u: u.multiplicator, user_models.values()),
                "delta_s": map(
                    lambda u: u.multiplicator_left_uncertainty + u.multiplicator_right_uncertainty,
                    user_models.values(),
                ),
                "tau": map(lambda u: u.translation, user_models.values()),
                "delta_tau": map(
                    lambda u: u.translation_left_uncertainty + u.translation_right_uncertainty,
                    user_models.values()
                )
            }
        )
        output.save_individual_scalings(scalings_df)

    @staticmethod
    def save_individual_scores(
        user_scorings: Mapping[int, ScoringModel],
        raw_user_scorings: Mapping[int, ScoringModel],
        voting_rights: VotingRights,
        output: PipelineOutput,
    ):
        scores_df = pd.DataFrame(
            data=[
                dict(
                    user_id=user_id,
                    entity_id=entity_id,
                    score=score,
                    uncertainty=left_unc+right_unc,
                    voting_right=voting_rights[user_id, entity_id],
                    raw_score=raw_scoring[0],
                    raw_uncertainty=raw_scoring[1] + raw_scoring[2]
                )
                for (user_id, scoring) in user_scorings.items()
                for (entity_id, (score, left_unc, right_unc)) in scoring.iter_entities()
                if (raw_scoring := raw_user_scorings[user_id](entity_id)) is not None
            ]
        )

        if len(scores_df) > 0:
            output.save_individual_scores(scores_df)


def trust_propagation_from_json(json):
    if json[0] == "TrustAll": 
        return TrustAll()
    if json[0] == "LipschiTrust": 
        return LipschiTrust(**json[1])
    if json[0] == "NoTrustPropagation":
        return NoTrustPropagation(**json[1])
    raise ValueError(f"TrustPropagation {json[0]} was not recognized")

def voting_rights_from_json(json):
    if json[0] == "AffineOvertrust": 
        return AffineOvertrust(**json[1])
    if json[0] == "IsTrust":
        return IsTrust(**json[1])
    raise ValueError(f"VotingRightsAssignment {json[0]} was not recognized")

def preference_learning_from_json(json):
    if json[0] == "UniformGBT": 
        return UniformGBT(**json[1])
    raise ValueError(f"PreferenceLearning {json[0]} was not recognized")

def scaling_from_json(json):
    if json[0] == "ScalingCompose": 
        return ScalingCompose(*[scaling_from_json(j) for j in json[1]])
    if json[0] == "Mehestan": 
        return Mehestan(**json[1])
    if json[0] == "QuantileZeroShift": 
        return QuantileZeroShift(**json[1])
    if json[0] == "NoScaling":
        return NoScaling()
    raise ValueError(f"Scaling {json[0]} was not recognized")

def aggregation_from_json(json):
    if json[0] == "StandardizedQrMedian": 
        return StandardizedQrMedian(**json[1])
    if json[0] == "StandardizedQrQuantile": 
        return StandardizedQrQuantile(**json[1])
    if json[0] == "Average":
        return Average()
    raise ValueError(f"Aggregation {json[0]} was not recognized")

def post_process_from_json(json):
    if json[0] == "Squash": 
        return Squash(**json[1])
    if json[0] == "NoPostProcess":
        return NoPostProcess()
    raise ValueError(f"PostProcess {json[0]} was not recognized")
    

def get_scorings_as_df(user_models: dict[int, ScoringModel]):
    return pd.DataFrame(
        data=[
            dict(
                user_id=user_id,
                entity_id=entity_id,
                score=score,
                uncertainty_left=left_unc,
                uncertainty_right=right_unc,
            )
            for (user_id, scoring) in user_models.items()
            for (entity_id, (score, left_unc, right_unc)) in scoring.iter_entities()
        ]
    )
