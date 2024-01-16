import logging

from solidago.trust_propagation import TrustPropagation
from solidago.voting_rights import VotingRights


logger = logging.getLogger(__name__)


class Pipeline:
    def __init__(
        self,
        trust_propagation: TrustPropagation,
        voting_rights: VotingRights,
        compute_scores: ComputeScores,
        to_display: ToDisplay
    ):
        self.trust_propagation = trust_propagation
        self.voting_rights = voting_rights
        self.compute_scores = compute_scores
        self.to_display = to_display
        
    def __call__(
        self,
        dataset: TournesolInput,
        criterion: Optional[Union[str, list[str]]] = None
    ):
        """ Run Pipeline """
        if criterion is None:
            criterion = set(data.comparisons["criteria"])
        if type(criterion) in (set, list, tuple):
            return { c: self(dataset, c) for c in criterion }
        
        logger.info("Starting Solidago pipeline for criterion '%s'", criterion)
        
        logger.info(f"Solidago pipeline: Propagating trust with {self.trust_propagation}")
        data.users = self.trust_propagation(data.users, data.vouches)
        
        logger.info(f"Solidago pipeline: Computing voting rights with {self.voting_rights}")
        data.voting_rights = self.voting_rights(data.users, data.vouches, data.comparisons)
    
        logger.info(f"Solidago pipeline: Computing scores with {self.compute_scores}")
        data.scores = self.compute_scores(data.voting_rights, data.entities, data.comparisons)
        
        logger.info(f"Solidago pipeline: Computing displayed scores with {self.to_display}")
        data.scores = self.to_display(data.scores)



        
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
    

