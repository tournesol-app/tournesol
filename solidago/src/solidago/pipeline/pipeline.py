import logging

from .trust_propagation import TrustPropagation
from .trust_propagation.lipschitrust import LipschiTrust
from .voting_rights_assignment import VotingRightsAssignment
from .voting_rights_assignment.limited_overtrust import VotingRightsWithLimitedOvertrust
from .user_models_inference import UserModelInference
from .user_models_inference.generalized_bradley_terry import UniformGBT
from .scaling import Scaling, ScalingCompose
from .scaling.mehestan import Mehestan
from .scaling.quantile_zero_shift import QuantileZeroShift
from .aggregation import Aggregation
from .aggregation.standardized_qrmed import QuantileStandardizedQrMed
from .post_process import PostProcess
from .post_process.squash import Squash

logger = logging.getLogger(__name__)


@classdata
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
    voting_rights: VotingRights = VotingRightsWithLimitedOvertrust(
        privacy_penalty=0.5, 
        min_overtrust=2.0,
        overtrust_ratio=0.1,
    )
    user_model_inference: UserModelInference = UniformGBT(
        comparison_max=10
    )
    scaling: Scaling = ScalingCompose(
        Mehestan(
            lipschitz=0.1,
            min_comparison=10,
            n_scalers_max=1000
        ),
        QuantileZeroShift(
            zero_quantile=0.15
        )
    )
    aggregation: Aggregation = QuantileStandardizedQrMed(
        qtl_std_dev=0.9,
        lipschitz=0.1
    )
    post_process: PostProcess = Squash()


class Pipeline:
    def __init__(
        self,
        trust_propagation: TrustPropagation = DefaultPipeline.trust_propagation,
        voting_rights: VotingRights = DefaultPipeline.voting_rights,
        user_model_inference: UserModelInference = DefaultPipeline.user_model_inference,
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
        user_model_inference: UserModelInference
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
        self.user_model_inference = user_model_inference
        self.scaling = scaling
        self.aggregation = aggregation
        self.post_process = post_process
        
    def __call__(
        self,
        dataset: TournesolInput,
        criterion: Optional[Union[str, list[str]]] = None
    ) -> tuple[list[UserModel], GlobalModel]:
        """ Run Pipeline """
        if criterion is None:
            criterion = set(data.comparisons["criteria"])
        if type(criterion) in (set, list, tuple):
            return { c: self(dataset, c) for c in criterion }
        
        logger.info("Starting the full Solidago pipeline for criterion '%s'", criterion)
        
        logger.info(f"Pipeline 1. Propagating trust with {self.trust_propagation}")
        data.users = self.trust_propagation(data.users, data.vouches)
        
        logger.info(f"Pipeline 2. Computing voting rights with {self.voting_rights}")
        data.voting_rights = self.voting_rights(data.users, data.vouches, data.comparisons)
    
        logger.info(f"Pipeline 3. Computing user models with {self.user_models}")
        data.user_models = self.user_model_inference(
            data.entities, data.comparisons, data.scores
        )
        
        logger.info(f"Pipeline 4. Collaborative score scaling with {self.scaling}")
        data.user_models = self.scaling(data.user_models, data.users)
        
        logger.info(f"Pipeline 5. Score aggregation with {self.aggregation}")
        data.gloal_model = self.aggregation(data.user_models)
                
        logger.info(f"Pipeline 6. Post-processing scores {self.score_post_process}")
        data.scores = self.score_post_process(data.scores)



        
        indiv_scores = get_individual_scores(input, criteria=criterion, parameters=parameters)
        logger.info("Computing individual scores for criterion '%s' DONE", criterion)
    
        logger.info("Computing individual scalings for criterion '%s'...", criterion)
        scalings = collaborative_scaling.compute_individual_scalings(
            individual_scores=indiv_scores,
            tournesol_input=input,
            W=parameters.W,
        )
        scaled_scores = collaborative_scaling.apply_scalings(
            individual_scores=indiv_scores,
            scalings=scalings
        )
    
        if len(scaled_scores) > 0:
            score_shift = collaborative_scaling.estimate_positive_score_shift(
                scaled_scores,
                W=parameters.score_shift_W,
                quantile=parameters.score_shift_quantile,
            )
            score_std = collaborative_scaling.estimate_score_deviation(
                scaled_scores,
                W=parameters.score_shift_W,
                quantile=parameters.score_deviation_quantile,
            )
            scaled_scores.score -= score_shift
            scaled_scores.score /= score_std
            scaled_scores.uncertainty /= score_std
    
        output.save_individual_scalings(scalings, criterion=criterion)
        logger.info("Computing individual scalings for criterion '%s' DONE", criterion)
    
        logger.info("Computing aggregated scores for criterion '%s'...", criterion)
        # Join ratings columns ("is_public", "trust_score", etc.)
        ratings = input.ratings_properties.set_index(["user_id", "entity_id"])
        scaled_scores = scaled_scores.join(
            ratings,
            on=["user_id", "entity_id"],
        )
    
        scaled_scores_with_voting_rights_per_score_mode = {
            mode: add_voting_rights(scaled_scores, params=parameters, score_mode=mode)
            for mode in ALL_SCORE_MODES
        }
        for mode in ALL_SCORE_MODES:
            scaled_scores_with_voting_rights = scaled_scores_with_voting_rights_per_score_mode[mode]
            global_scores = aggregate_scores(scaled_scores_with_voting_rights, W=parameters.W)
            global_scores["criteria"] = criterion
    
            # Apply squashing
            squash_function = get_squash_function(parameters)
            global_scores["uncertainty"] = 0.5 * (
                squash_function(global_scores["score"] + global_scores["uncertainty"])
                - squash_function(global_scores["score"] - global_scores["uncertainty"])
            )
            global_scores["score"] = squash_function(global_scores["score"])
    
            logger.info(
                "Mehestan: scores computed for crit '%s' and mode '%s'",
                criterion,
                mode,
            )
            output.save_entity_scores(global_scores, criterion=criterion, score_mode=mode)
        logger.info("Computing aggregated scores for criterion '%s' DONE", criterion)
    
        logger.info("Computing squashed individual scores for criterion '%s'...", criterion)
        squash_function = get_squash_function(parameters)
        scaled_scores = scaled_scores_with_voting_rights_per_score_mode["default"]
        scaled_scores["uncertainty"] = 0.5 * (
            squash_function(scaled_scores["score"] + scaled_scores["uncertainty"])
            - squash_function(scaled_scores["score"] - scaled_scores["uncertainty"])
        )
        scaled_scores["score"] = squash_function(scaled_scores["score"])
        scaled_scores["criteria"] = criterion
        output.save_individual_scores(scaled_scores, criterion=criterion)
        logger.info("Computing squashed individual scores for criterion '%s' DONE", criterion)
    
        logger.info(
            "Solidago pipeline for criterion '%s' DONE.",
            criterion,
        )
    
        return output
    

