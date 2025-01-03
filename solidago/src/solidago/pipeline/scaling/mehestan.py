from typing import Callable, Optional, Iterable

import numpy as np
import pandas as pd
import timeit
import logging

logger = logging.getLogger(__name__)

from solidago.primitives import qr_median, qr_uncertainty, lipschitz_resilient_mean
from solidago.primitives.pairs import UnorderedPairs
from solidago.primitives.datastructure import NestedDictOfRowList
from solidago.state import *

from .base import Scaling
from .no_scaling import NoScaling


class Mehestan(Scaling):
    def __init__(
        self, 
        lipschitz=0.1, 
        min_activity=10.0,
        n_scalers_max=100, 
        privacy_penalty=0.5,
        user_comparison_lipschitz=10.0,
        p_norm_for_multiplicative_resilience=4.0,
        n_entity_to_fully_compare_max=100,
        n_diffs_sample_max=1000,
        error=1e-5
    ):
        """ Mehestan performs Lipschitz-resilient collaborative scaling.
        It is based on "Robust Sparse Voting", by Youssef Allouah, 
        Rachid Guerraoui, Lȩ Nguyên Hoang and Oscar Villemaud, 
        published at AISTATS 2024.
        
        The inclusion of uncertainties is further detailed in
        "Solidago: A Modular Pipeline for Collaborative Scoring",
        by Lê Nguyên Hoang, Romain Beylerian, Bérangère Colbois, Julien Fageot, 
        Louis Faucon, Aidan Jungo, Alain Le Noac'h, Adrien Matissart
        and Oscar Villemaud.
        
        Parameters
        ----------
        lipschitz: float
            Resilience parameters. Larger values are more resilient, but less accurate.
        min_n_comparison: float
            Minimal number of comparisons to be a potential scaler
        n_scalers_max: float
            Maximal number of scalers
        privacy_penalty: float
            Penalty to private ratings when selecting scalers
        p_norm_for_multiplicative_resilience: float
            To provide stronger security, 
            we enforce a large resilience on multiplicator estimation,
            when the model scores of a user are large.
            The infinite norm may be to sensitive to extreme values,
            thus we propose to use an l_p norm.
        error: float
            Error bound
        """
        self.lipschitz = lipschitz
        self.min_activity = min_activity
        self.n_scalers_max = n_scalers_max
        self.privacy_penalty = privacy_penalty
        self.user_comparison_lipschitz = user_comparison_lipschitz
        self.p_norm_for_multiplicative_resilience = p_norm_for_multiplicative_resilience
        self.n_entity_to_fully_compare_max = n_entity_to_fully_compare_max
        self.n_diffs_sample_max = n_diffs_sample_max
        self.error = error

    def main(self, 
        users: Users,
        entities: Entities,
        made_public: MadePublic,
        user_models: UserModels,
    ) -> tuple[Users, UserModels]:
        """ Returns scaled user models
        
        Returns
        -------
        users: Users
            Records whether users are Mehestan-scalers
        user_models: ScoringModel
            Scaled user models
        """
        logger.info("Starting Mehestan's collaborative scaling")
        user_name2index = { str(user): index for index, user in enumerate(users) }

        logger.info("Mehestan 0. Compute user scores")
        scores = user_models.score(entities).reorder_keys(["criterion", "username", "entity_name"])
        logger.info(f"Mehestan 0. Terminated")
        
        scales = ScaleDict(key_names=["criterion", "username"])
        for criterion in scores.get_set("criterion"):
            start = timeit.default_timer()
            logger.info("Mehestan 1. Select scalers based on activity and trustworthiness")
            users["is_scaler"] = self.compute_scalers(users, made_public, scores[criterion])
            if len(scalers) == 0:
                logger.warning("    No user qualifies as a scaler. No scaling performed.")
                logger.info(f"Mehestan 1. Terminated in {int(end_step1 - start)} seconds")
                return user_models
            end_step1 = timeit.default_timer()
            logger.info(f"Mehestan 1. Terminated in {int(end_step1 - start)} seconds")
    
            logger.info("Mehestan 2. Collaborative scaling of scalers")
            scalers = users.get({ "is_scaler": True })
            scaler_scores = scores[criterion][scalers]
            scaler_scales = self.scale_scalers(scalers, made_public, scaler_scores)
            scales[criterion] = scaler_scales
            end_step2 = timeit.default_timer()
            logger.info(f"Mehestan 2. Terminated in {int(end_step2 - end_step1)} seconds")
    
            logger.info("Mehestan 3. Scaling of non-scalers")
            scales[criterion] = scaler_scales | self.scale_non_scalers(users, made_public, 
                scores[criterion], scaler_scales)
            end = timeit.default_timer()
            logger.info(f"Mehestan 3. Terminated in {int(end - end_step2)} seconds")
    
            logger.info(f"Succesful Mehestan normalization, in {int(end - start)} seconds")
        return scaled_models

    ############################################
    ##  The three main steps are              ##
    ##  1. Select the subset of scalers       ##
    ##  2. Scale the scalers                  ##
    ##  3. Fit the nonscalers to the scalers  ##
    ############################################

    def compute_scalers(self,
        users: Users, 
        made_public: MadePublic,
        scores: MultiScore, # key_names = ["username", "entity_name"]
    ) -> np.ndarray:
        """ Determines which users will be scalers.
        The set of scalers is restricted for two reasons.
        First, too inactive users are removed, because their lack of comparability
        with other users makes the scaling process ineffective.
        Second, scaling scalers is the most computationally demanding step of Mehestan.
        Reducing the number of scalers accelerates the computation (often a bottleneck).
            
        Returns
        -------
        is_scaler: np.ndarray
            is_scaler[i] says whether username at iloc i in users is a scaler
        """
        activities = self.compute_activities(users, made_public, scores)
        argsort = np.argsort(activities)
        is_scaler = np.array([False] * len(np_activities))
        for user_index in range(min(self.n_scalers_max, len(np_activities))):
            if np_activities[argsort[-user_index-1]] < self.min_activity:
                break
            is_scaler[argsort[-user_index-1]] = True
        return is_scaler

    def scale_scalers(self, 
        scalers: Users,
        made_public: MadePublic, 
        scores: MultiScore, # key_names == ["username", "entity_name"]
    ) -> ScaleDict:
        """ Scale scalers
        
        Parameters
        ----------
        scalers: Users
            Must have column "is_scaler"
        made_public: MadePublic
        scores: MultiScore
            Must have key_names == ["username", "entity_name"]
            Should be processed to only consider scalers' names as username
        
        Returns
        -------
        scales: ScaleDict
            With key_names = ["username"] and processed values tuple[Score, Score],
            which correspond to the multiplicator and the translation.
        """
        start = timeit.default_timer()
        model_norms = self.compute_model_norms(scalers, made_public, scores)
        end2a = timeit.default_timer()
        logger.info(f"    Mehestan 2a. Model norms in {int(end2a - start)} seconds")

        weights, ratios = self.compute_entity_ratios(scalers, scalers, made_public, scores)
        end2b = timeit.default_timer()
        logger.info(f"    Mehestan 2b. Entity ratios in {int(end2b - end2a)} seconds")
        ratio_voting_rights, ratios, ratio_uncertainties = _aggregate_user_comparisons(
            scalers, entity_ratios, 
            error=self.error, lipschitz=self.user_comparison_lipschitz
        )
        end2c = timeit.default_timer()
        logger.info(f"    Mehestan 2c. Aggregate ratios in {int(end2c - end2b)} seconds")
        multiplicators = self.compute_multiplicators(
            ratio_voting_rights, ratios, ratio_uncertainties, model_norms
        )
        end2d = timeit.default_timer()
        logger.info(f"    Mehestan 2d. Multiplicators in {int(end2d - end2c)} seconds")

        entity_diffs = self.compute_entity_diffs(
            user_models, user_models, entities, privacy, multiplicators
        )
        end2e = timeit.default_timer()
        logger.info(f"    Mehestan 2e. Entity diffs in {int(end2e - end2d)} seconds")
        diff_voting_rights, diffs, diff_uncertainties = _aggregate_user_comparisons(
            scalers, entity_diffs, 
            error=self.error, lipschitz=self.user_comparison_lipschitz
        )
        end2f = timeit.default_timer()
        logger.info(f"    Mehestan 2f. Aggregate diffs in {int(end2f - end2e)} seconds")
        translations = self.compute_translations(diff_voting_rights, diffs, diff_uncertainties)
        end2g = timeit.default_timer()
        logger.info(f"    Mehestan 2g. Translations in {int(end2g - end2f)} seconds")

        return { 
            u: ScaledScoringModel(
                base_model=model,
                multiplicator=multiplicators[u][0], 
                translation=translations[u][0],
                multiplicator_left_uncertainty=multiplicators[u][1], 
                multiplicator_right_uncertainty=multiplicators[u][1], 
                translation_left_uncertainty=translations[u][1],
                translation_right_uncertainty=translations[u][1]
            ) for u, model in user_models.items()
        }

    def scale_non_scalers(
        self, user_models, nonscalers, entities, scalers, scaled_models, privacy
    ):
        start = timeit.default_timer()
        model_norms = self.compute_model_norms(user_models, nonscalers, entities, privacy)
        end2a = timeit.default_timer()
        logger.info(f"    Mehestan 3a. Model norms in {int(end2a - start)} seconds")

        end3a = timeit.default_timer()
        nonscaler_models = {u: m for (u, m) in user_models.items() if u in nonscalers.index}
        entity_ratios = self.compute_entity_ratios(
            nonscaler_models, scaled_models, entities, privacy
        )
        end3b = timeit.default_timer()
        logger.info(f"    Mehestan 3b. Entity ratios in {int(end3b - end3a)} seconds")
        ratio_voting_rights, ratios, ratio_uncertainties = _aggregate_user_comparisons(
            scalers, entity_ratios, error=self.error, lipschitz=self.user_comparison_lipschitz
        )
        end3c = timeit.default_timer()
        logger.info(f"    Mehestan 3c. Aggregate ratios in {int(end3c - end3b)} seconds")
        multiplicators = self.compute_multiplicators(
            ratio_voting_rights, ratios, ratio_uncertainties, model_norms
        )
        end3d = timeit.default_timer()
        logger.info(f"    Mehestan 3d. Multiplicators in {int(end3d - end3c)} seconds")

        entity_diffs = self.compute_entity_diffs(
            nonscaler_models, scaled_models, entities, privacy, multiplicators
        )
        end3e = timeit.default_timer()
        logger.info(f"    Mehestan 3e. Entity diffs in {int(end3e - end3d)} seconds")
        diff_voting_rights, diffs, diff_uncertainties = _aggregate_user_comparisons(
            scalers, entity_diffs, error=self.error, lipschitz=self.user_comparison_lipschitz
        )
        end3f = timeit.default_timer()
        logger.info(f"    Mehestan 3f. Aggregate diffs in {int(end3f - end3e)} seconds")
        translations = self.compute_translations(diff_voting_rights, diffs, diff_uncertainties)
        end3g = timeit.default_timer()
        logger.info(f"    Mehestan 3g. Translations in {int(end3g - end3f)} seconds")

        return scaled_models | {
            u: ScaledScoringModel(
                base_model=model,
                multiplicator=multiplicators[u][0],
                translation=translations[u][0],
                multiplicator_left_uncertainty=multiplicators[u][1],
                multiplicator_right_uncertainty=multiplicators[u][1],
                translation_left_uncertainty=translations[u][1],
                translation_right_uncertainty=translations[u][1],
            )
            for u, model in nonscaler_models.items()
        }

    ############################################
    ##     Methods to esimate the scalers     ##
    ############################################

    def compute_activities(self,
        users: Users, 
        made_public: MadePublic,
        scores: MultiScore, # key_names == ["username", "entity_name"]
    ) -> np.ndarray:
        """ Returns a dictionary, which maps users to their trustworthy activeness.
        
        Parameters
        ----------
        users: Users
        made_public: MadePublic
            Must have key_names "username" and "entity_name"
        scores: MultiScore
            Must have key_names == ["username", "entity_name"]
    
        Returns
        -------
        activities: np.ndarray
            activities[i] is a measure of user i's trustworthy activeness,
            where i is the iloc of the user in users
        """
        made_public = made_public.reorder_keys(["username", "entity_name"])
        return np.array([
            self.computer_user_activities(made_public[user], scores[user])
            for user in users
        }]
    
    def computer_user_activities(self,
        made_public: MadePublic, # key_names = ["entity_name"]
        scores: MultiScore, # key_names = ["entity_name"]
    ) -> float:
        """ Returns a dictionary, which maps users to their trustworthy activeness.
        
        Parameters
        ----------
        made_public: MadePublic with key_names = ["entity_name"]
        scores: MultiScore with key_names = ["entity_name"]
    
        Returns
        -------
        activity: float
        """
        if trust_score <= 0.0:
            return 0.0
            
        return trust_score * sum([
            1 if made_public[entity] else privacy_penalty
            for entity, score in scores
            if not (score.min < 0 and score.max > 0)
        ])

    ############################################
    ##  Methods to esimate the multiplicators ##
    ############################################

    def compute_model_norms(self,
        users: Users,
        made_public: MadePublic, # key_names == ["username", "entity_name"]
        scores: MultiScore, # key_names == ["username", "entity_name"]
    ) -> np.ndarray:
        """ Estimator of the scale of scores of a user, with an emphasis on large scores.
        The estimator uses a L_power norm, and weighs scores, depending on public/private status.
        For each user u, it computes (sum_e w[ue] * score[u, e]**power / sum_e w[ue])**(1/power).
        
        Parameters
        ----------
        users: Users
        made_public: MadePublic
            Must have key_names == ["username", "entity_name"]
        scores: MultiScore
            Must have key_names == ["username", "entity_name"]
    
        Returns
        -------
        out: np.ndarray
            out[i] is the norm of user i's score vector, where i is the user's iloc in users
        """
        return [ self.compute_model_norm(made_public[user], scores[user]) for user in users ]

    def compute_model_norm(self, made_public: MadePublic, scores: MultiScore) -> float:
        """ Estimator of the scale of scores of a user, with an emphasis on large scores.
        The estimator uses a L_power norm, and weighs scores, depending on public/private status.
        For each user u, it computes (sum_e w[ue] * score[u, e]**power / sum_e w[ue])**(1/power).
        
        Parameters
        ----------
        made_public: MadePublic
            Must have key_names == ["entity_name"]
        scores: MultiScore
            Must have key_names == ["entity_name"]
    
        Returns
        -------
        norm: float
        """
        weight_sum, weighted_sum = 0., 0.
        for entity_name, score in scores:
            weight = self.penalty(made_public[entity_name])
            weight_sum += weight
            weighted_sum += weight * (score.value**self.p_norm_for_multiplicative_resilience)
    
        if weight_sum == 0:
            return 1.0
    
        return np.power(weighted_sum / weight_sum, 1 / self.p_norm_for_multiplicative_resilience)

    def compute_entity_ratios(self, 
        scalees: Users, 
        scalers: Users, 
        made_public: MadePublic, # key_names == ["username", "entity_name"]
        scalee_scores: MultiScore, # key_names == ["username", "entity_name"]
        scaler_scores: MultiScore, # key_names == ["username", "entity_name"]
    ) -> tuple[VotingRights, NestedDictOfRowLists]: # key_names == ["scalee_name", "scaler_name"]
    # ) -> dict[int, dict[int, tuple[list[float], list[float], list[float], list[float]]]]:
        """ Computes the ratios of score differences, with uncertainties,
        for comparable entities of any pair of scalers (s_{uvef} in paper),
        for u in scalees and v in scalers.
        Note that the output rations[u][v] is given as a 1-dimensional np.ndarray
        without any reference to e and f.
        
        Parameters
        ----------
        scalees: Users, 
        scalers: Users, 
        made_public: MadePublic
            Must have key_names == ["username", "entity_name"]
        scalee_scores: MultiScore
            Must have key_names == ["username", "entity_name"]
        scaler_scores: MultiScore
            Must have key_names == ["username", "entity_name"]
        
        Returns
        -------
        voting_rights: VotingRights
            With key_names == ["scalee_name", "scaler_name"]
            voting_rights[scalee_name, scaler_name] is the weight of scaler_name
            on the multiplicative scaling of scalee_name        
        ratios: NestedDictOfRowLists
            With key_names == ["scalee_name", "scaler_name"]
            multiscore[scalee_name, scaler_name] is a list of rows,
            where each row is a ratio of score differences,
            and left and right are the left and right ratio uncertainties.
        """
        reordered_scaler_scores = scaler_scores.reorder_keys(["entity_name", "username"])
        voting_rights = VotingRights()
        ratios = NestedDictOfRowList()
        
        for scalee in scalees:
            scalee_entity_names = scalee_scores[scalee].get_set("entity_name")
            scalers = reordered_scaler_scores[scalee_entity_names].get_set("username")
        
            for scaler in scalers:
                
                if str(scalee) == str(scaler):
                    voting_rights[scalee, scaler] = 1
                    ratios[scalee, scaler] = [Score(1, 0, 0).to_dict()]
                    continue
                
                common_entity_names = scalee_entity_names & scaler_scores[scaler].get_set("entity_name")
                
                if len(common_entity_names) <= 1:
                    continue
                if len(common_entity_names) <= self.n_entity_to_fully_compare_max:
                    pairs = UnorderedPairs(common_entity_names)
                else:
                    pairs = UnorderedPairs(common_entity_names).n_samples(self.n_diffs_sample_max)
                
                voting_right, ratio_list = self.compute_ratios(
                    scalee_scores[scalee], 
                    scaler_scores[scaler], 
                    made_public[scaler],
                    pairs
                )
                if voting_right > 0:
                    voting_rights[scalee, scaler] = voting_right
                    ratios[scalee, scaler] = ratio_list
                
        return voting_rights, ratios

    def compute_ratios(self,
        scalee_scores: MultiScore, # key_name == ["entity_name"]
        scaler_scores: MultiScore, # key_name == ["entity_name"]
        scaler_public: MadePublic, # key_name == ["entity_name"]
        pairs: Iterable # outputs list of pairs (e, f) of entity names
    ) -> tuple[float, list[dict]]:
        """ Returns the scaler's voting right and ratios to multiplicatively scale scalee's model """
        voting_right, ratios = 0, list()
        for e, f in pairs:
            ratio = (scaler_scores[e] - scaler_scores[f]) / (scalee_scores[e] - scalee_scores[f])
            if ratio.isnan(): continue
            ratios.append(ratio.abs())
            voting_right += self.penalty(scaler_public[e]) * self.penalty(scaler_public[f])
        return voting_right, ratios
    
    def penalty(self, public: bool):
        return 1 if public else self.privacy_penalty

    def compute_multiplicators(
        self, 
        voting_rights: dict[int, list[float]], 
        ratios: dict[int, list[float]], 
        uncertainties: dict[int, list[float]],
        model_norms: dict[int, float]
    ) -> dict[int, tuple[float, float]]:
        """ Computes the multiplicators of users with given user_ratios
        
        Parameters
        ----------
        ratios: dict[int, tuple[list[float], list[float], list[float]]]
            ratios[u][0] is a list of voting rights
            ratios[u][1] is a list of ratios
            ratios[u][2] is a list of (symmetric) uncertainties
        model_norms: dict[int, float]
            model_norms[u] estimates the norm of user u's score model
            
        Returns
        -------
        multiplicators: dict[int, tuple[float, float]]
            multiplicators[user][0] is the multiplicative scaling of user
            multiplicators[user][1] is the uncertainty on the multiplicator
        """
        return {
            u: _aggregate(self.lipschitz / (8 * (1e-9 + model_norms[u])), 
                voting_rights[u], ratios[u], uncertainties[u], 
                default_value=1.0, default_dev=0.8, error=self.error)
            for u in voting_rights
        }

    ############################################
    ##   Methods to esimate the translations  ##
    ############################################

    def compute_entity_diffs(
        self, 
        scalee_models: dict[int, ScoringModel],
        scaler_models: dict[int, ScoringModel],
        entities: pd.DataFrame,
        privacy: PrivacySettings,
        multiplicators: dict[int, tuple[float, float]]
    ) -> dict[int, dict[int, tuple[list[float], list[float], list[float], list[float]]]]:
        """ Computes the ratios of score differences, with uncertainties,
        for comparable entities of any pair of scalers (s_{uvef} in paper).
        Note that the output rations[u][v] is given as a 1-dimensional np.ndarray
        without any reference to e and f.
        
        Parameters
        ----------
        user_models: dict[int, ScoringModel]
            user_models[user] is user's scoring model
        scalees: DataFrame with columns
            * user_id (int, index)
        scalers: DataFrame with columns
            * user_id (int, index)
        entities: DataFrame with columns
            * entity_id (int, index)
        multiplicators: dict[int, tuple[float, float]]
            multiplicators[user][0] is the multiplicative scaling of user
            multiplicators[user][1] is the uncertainty on the multiplicator
        
        Returns
        -------
        out: dict[int, dict[int, tuple[list[float], list[float], list[float]]]]
            out[user][user_bis] is a tuple (differences, lefts, rights),
            where differences has score differences,
            and left and right are the left and right ratio uncertainties.
        """
        differences = dict()
        entities_ids = set(entities.index)

        for u, u_model in scalee_models.items():
            u_entities = entities_ids & u_model.scored_entities()
            differences[u] = dict()
            for v, v_model in scaler_models.items():
                if u == v:
                    differences[u][v] = [0.], [1.], [0.], [0.]
                    continue

                uv_entities = u_entities & v_model.scored_entities()
                if len(entities) == 0:
                    continue

                differences[u][v] = list(), list(), list(), list()              
                for e in uv_entities:
                    score_u, left_u, right_u = u_model(e, entities.loc[e])
                    score_v, left_v, right_v = v_model(e, entities.loc[e])

                    uve_voting_right = 1
                    if privacy is not None and privacy[u, e]:
                        uve_voting_right *= self.privacy_penalty
                    if privacy is not None and privacy[v, e]:
                        uve_voting_right *= self.privacy_penalty

                    u_multiplicator = (1., 0., 0.) if u not in multiplicators else multiplicators[u]
                    v_multiplicator = (1., 0., 0.) if v not in multiplicators else multiplicators[v]

                    differences[u][v][0].append(
                        v_multiplicator[0] * score_v - u_multiplicator[0] * score_u
                    )
                    differences[u][v][1].append(uve_voting_right)
                    differences[u][v][2].append(
                        u_multiplicator[0] * left_u
                        + u_multiplicator[1] * score_u * (score_u > 0)
                        - u_multiplicator[1] * score_u * (score_u < 0)
                        + v_multiplicator[0] * left_v
                        + v_multiplicator[1] * score_v * (score_v > 0)
                        - v_multiplicator[1] * score_v * (score_v < 0)
                    )
                    differences[u][v][3].append(
                        u_multiplicator[0] * right_u
                        - u_multiplicator[1] * score_u * (score_u < 0)
                        + u_multiplicator[1] * score_u * (score_u > 0)
                        + v_multiplicator[0] * right_v
                        - v_multiplicator[1] * score_v * (score_v < 0)
                        + v_multiplicator[1] * score_v * (score_v > 0)
                    )

        return differences

    def compute_translations(
        self, 
        voting_rights: dict[int, list[float]], 
        diffs: dict[int, list[float]], 
        uncertainties: dict[int, list[float]]
    ) -> dict[int, tuple[float, float]]:
        """ Computes the multiplicators of users with given user_ratios
        
        Parameters
        ----------
        diffs: dict[int, tuple[list[float], list[float], list[float]]]
            diffs[u][0] is a list of voting rights
            diffs[u][1] is a list of ratios
            diffs[u][2] is a list of (symmetric) uncertainties
            
        Returns
        -------
        translations: dict[int, tuple[float, float]]
            translations[user][0] is the multiplicative scaling of user
            translations[user][1] is the uncertainty on the multiplicator
        """
        return {
            u: _aggregate(self.lipschitz / 8, 
                voting_rights[u], diffs[u], uncertainties[u], 
                default_value=0.0, default_dev=1.0,
                error=self.error, aggregator=lipschitz_resilient_mean)
            for u in voting_rights
        }

    def to_json(self):
        return type(self).__name__, dict(
            lipschitz=self.lipschitz, 
            min_activity=self.min_activity, 
            n_scalers_max=self.n_scalers_max, 
            privacy_penalty=self.privacy_penalty,
            p_norm_for_multiplicative_resilience=self.p_norm_for_multiplicative_resilience,
            error=self.error
        )

    def __str__(self):
        prop_names = ["lipschitz", "min_activity", "n_scalers_max", "privacy_penalty",
            "user_comparison_lipschitz", "p_norm_for_multiplicative_resilience", "error"]
        prop = ", ".join([f"{p}={getattr(self, p)}" for p in prop_names])
        return f"{type(self).__name__}({prop})"

##############################################
## Preprocessing to facilitate computations ##
##############################################

def _compute_abs_diff(
    user_model: ScoringModel, 
    entity_a: int, 
    entity_b: int, 
    entities: pd.DataFrame
) -> Optional[tuple[float, float, float]]:
    output_a = user_model(entity_a, 
    entities.loc[entity_a])
    if output_a is None:
        return None
    output_b = user_model(entity_b, entities.loc[entity_b])
    if output_b is None:
        return None
        
    score_a, left_a, right_a = output_a
    score_b, left_b, right_b = output_b
    if score_a - score_b >=  2 * left_a + 2 * right_b:
        return score_a - score_b, left_a + right_b, right_a + left_b
    if score_b - score_a >= 2 * left_b + 2 * right_a:
        return score_b - score_a, left_b + right_a, right_b + left_a
    return None



def _aggregate_user_comparisons(
    scalers: pd.DataFrame, 
    scaler_comparisons,
    error: float=1e-5,
    lipschitz: float=1.0
) -> tuple[
    dict[int, list[float]],
    dict[int, list[float]],
    dict[int, list[float]],
]:
    """ For any two pairs (scalee, scaler), aggregates their comparative data.
    Typically used to transform s_{uvef}'s into s_{uv}, and tau_{uve}'s into tau_{uv}.
    The reference to v is also lost in the process, as it is then irrelevant.
    
    Parameters
    ----------
    scalers: DataFrame with columns
        * user_id (int, index)
        * trust_score (float)
    scaler_comparisons: dict[int, dict[int, tuple[list[float], list[float], list[float]]]]
        scaler_comparisons[user][user_bis] is a tuple (voting_rights, values, lefts, rights).
        values, lefts and rights are lists of floats of the same lengths.
        
    Returns
    -------
    voting_rights: dict[int, list[float]]
    comparisons: dict[int, list[float]]
    uncertainties: dict[int, list[float]
    """
    voting_rights, comparisons, uncertainties = dict(), dict(), dict()
    
    for u in scaler_comparisons:
        voting_rights[u], comparisons[u], uncertainties[u] = list(), list(), list()
        for v in scaler_comparisons[u]:
                            
            voting_rights[u].append(
                scalers.loc[v, "trust_score"] if "trust_score" in scalers else 1.0
            )
            comparisons[u].append(qr_median(
                lipschitz=lipschitz, 
                values=np.array(scaler_comparisons[u][v][0]),
                voting_rights=np.array(scaler_comparisons[u][v][1]), 
                left_uncertainties=np.array(scaler_comparisons[u][v][2]),
                right_uncertainties=np.array(scaler_comparisons[u][v][3]),
                error=error
            ))
            uncertainties[u].append(qr_uncertainty(
                lipschitz=lipschitz, 
                values=np.array(scaler_comparisons[u][v][0]),
                voting_rights=np.array(scaler_comparisons[u][v][1]), 
                left_uncertainties=np.array(scaler_comparisons[u][v][2]),
                right_uncertainties=np.array(scaler_comparisons[u][v][3]),
                default_dev=1.0,
                error=error,
                median=comparisons[u][-1]
            ))
            
    return voting_rights, comparisons, uncertainties

def _aggregate(
    lipschitz: float,
    voting_rights: list[float],
    values: list[float],
    uncertainties: list[float],
    default_value: float,
    error: float=1e-5,
    aggregator: Callable = qr_median,
    default_dev: float=1.0,
) -> tuple[float, float]:
    """ Computes the multiplicators of users with given user_ratios
    
    Parameters
    ----------
    values: tuple[list[float], list[float], list[float]]
        values[0] is a list of voting rights
        values[1] is a list of ratios
        values[2] is a list of (symmetric) uncertainties
    model_norms: dict[int, float]
        model_norms[u] estimates the norm of user u's score model
        
    Returns
    -------
    multiplicators: dict[int, tuple[float, float]]
        multiplicators[user][0] is the multiplicative scaling of user
        multiplicators[user][1] is the uncertainty on the multiplicator
    """
    value = aggregator(
        lipschitz=lipschitz, 
        values=np.array(values),
        voting_rights=np.array(voting_rights), 
        left_uncertainties=np.array(uncertainties),
        right_uncertainties=np.array(uncertainties),
        default_value=default_value,
        error=error
    )
    uncertainty = qr_uncertainty(
        lipschitz=lipschitz, 
        voting_rights=np.array(voting_rights),
        values=np.array(values), 
        left_uncertainties=np.array(uncertainties),
        right_uncertainties=np.array(uncertainties),
        default_dev=default_dev,
        error=error,
        median=value if aggregator is qr_median else None,
    )
    return value, uncertainty
