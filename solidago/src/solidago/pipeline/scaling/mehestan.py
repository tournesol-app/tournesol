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
        default_multiplicator_dev=0.8,
        default_translation_dev=1.,
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
        self.default_multiplicator_dev = default_multiplicator_dev
        self.default_translation_dev = default_translation_dev
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
            scale_scalers_output = self.scale_scalers(scalers, made_public, scaler_scores)
            multiplicators, translations, scaler_scores = scale_scalers_output
            for scaler_name in multiplicators:
                scales[criterion, scaler_name] = (
                    *multiplicators[scaler_name].to_triplet(), 
                    *translations[scaler_name].to_triplet()
                )
            end_step2 = timeit.default_timer()
            logger.info(f"Mehestan 2. Terminated in {int(end_step2 - end_step1)} seconds")
    
            logger.info("Mehestan 3. Scaling of non-scalers")
            scales[criterion] = scaler_scales | self.scale_non_scalers(users, made_public, 
                scores[criterion], scaler_scales)
            end = timeit.default_timer()
            logger.info(f"Mehestan 3. Terminated in {int(end - end_step2)} seconds")
            
            logger.info(f"Succesful Mehestan normalization, in {int(end - start)} seconds")
        return scaled_models

    def penalty(self, public: bool):
        return 1 if public else self.privacy_penalty

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
        scaler_scores: MultiScore, # key_names == ["username", "entity_name"]
    ) -> [MultiScore, MultiScore, MultiScore]:
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
        model_norms = self.compute_model_norms(scalers, made_public, scaler_scores)
        end2a = timeit.default_timer()
        logger.info(f"    Mehestan 2a. Model norms in {int(end2a - start)} seconds")

        weight_lists, ratio_lists = self.compute_entity_ratios(scalers, scalers, made_public, 
            scaler_scores, scaler_scores)
        end2b = timeit.default_timer()
        logger.info(f"    Mehestan 2b. Entity ratios in {int(end2b - end2a)} seconds")
        voting_rights, ratios = self.aggregate_scaler_scores(scalers, weight_lists, ratio_lists)
        end2c = timeit.default_timer()
        logger.info(f"    Mehestan 2c. Aggregate ratios in {int(end2c - end2b)} seconds")
        multiplicators = self.compute_multiplicators(voting_rights, ratios, model_norms)
        end2d = timeit.default_timer()
        logger.info(f"    Mehestan 2d. Multiplicators in {int(end2d - end2c)} seconds")

        for (scaler_name, entity_name), score in scaler_scores:
            scaler_scores[scaler_name, entity_name] = score * multiplicators[scaler_name]
        
        weight_lists, diff_lists = self.compute_entity_diffs(scalers, scalers, made_public, 
            scaler_scores, scaler_scores)
        end2e = timeit.default_timer()
        logger.info(f"    Mehestan 2e. Entity diffs in {int(end2e - end2d)} seconds")
        voting_rights, diffs = self.aggregate_scaler_scores(scalers, weight_lists, diff_lists)
        end2f = timeit.default_timer()
        logger.info(f"    Mehestan 2f. Aggregate diffs in {int(end2f - end2e)} seconds")
        translations = self.compute_translations(voting_rights, diffs)
        end2g = timeit.default_timer()
        logger.info(f"    Mehestan 2g. Translations in {int(end2g - end2f)} seconds")

        return multiplicators, translations, scaler_scores

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
    ##    Methods to estimate the scalers     ##
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

    #############################################################
    ##  Methods used for both multiplicators and translations  ##
    #############################################################
    
    def aggregate_scaler_scores(self,
        scalers: Users,
        weight_lists: NestedDictOfRowList, # key_names == ["scalee_name", "scaler_name"]
        score_lists: NestedDictOfRowList, # key_names == ["scalee_name", "scaler_name"]
    ) -> tuple[VotingRights, MultiScore]: # key_names == ["scalee_name", "scaler_name"]
        """ For any two pairs (scalee, scaler), aggregates their ratio or diff data.
        Typically used to transform s_{uvef}'s into s_{uv}, and tau_{uve}'s into tau_{uv}.
        The reference to v is also lost in the process, as it is then irrelevant.
        
        Parameters
        ----------
        voting_rights: VotingRights
            Must have key_names == ["scalee_name", "scaler_name"]
            voting_rights[scalee_name, scaler_name] is a list of weights
        comparisons: NestedDictOfRowList
            Must have key_names == ["scalee_name", "scaler_name"]
            comparisons[scalee, scaler] is a list of triplets that represent a Score,
            which represent how scalee's scale should be set to match scaler's.
            
        Returns
        -------
        voting_rights: VotingRights
            With key_names == ["scalee_name", "scaler_name"]
        multiscores: MultiScore
            With key_names == ["scalee_name", "scaler_name"]
        """
        voting_rights = VotingRights(key_names=["scalee_name", "scaler_name"])
        multiscores = MultiScore(key_names=["scalee_name", "scaler_name"])
        
        for (scalee_name, scaler_name), score_list in score_lists:
            kwargs = dict(
                lipschitz=self.user_comparison_lipschitz, 
                values=np.array([ score.value for score in score_list ]),
                voting_rights=np.array(weight_lists[scalee_name, scaler_name]),
                left_uncertainties=np.array([ score.left_unc for score in score_list ]),
                right_uncertainties=np.array([ score.right_unc for score in score_list ]),
                error=self.error
            )
            value = qr_median(**kwargs)
            uncertainty = qr_uncertainty(median=value, **kwargs)
            multiscores[scalee_name, scaler_name] = Score(value, uncertainty, uncertainty)
            
            if "trust_score" in scalers:
                voting_rights[scalee_name, scaler_name] = scalers.loc[scaler_name, "trust_score"]
            else:
                voting_rights[scalee_name, scaler_name] = 1.
                
        return voting_rights, multiscores

    def aggregate_scalers(self,
        voting_rights: VotingRights, # key_names = ["scaler_name"]
        multiscore: MultiScore, # key_names = ["scaler_name"]
        lipschitz: float,
        default_value: float, 
        default_dev: float, 
        aggregator: Callable = qr_median,
    ) -> Score:
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
        kwargs = dict(
            lipschitz=lipschitz, 
            voting_rights=np.array([ voting_right for scaler_name, voting_right in voting_rights ]),
            values=np.array([ score.value for scaler_name, score in multiscore ]),
            left_uncertainties=np.array([ score.left_unc for scaler_name, score in multiscore ]),
            right_uncertainties=np.array([ score.right_unc for scaler_name, score in multiscore ]),
            default_value=default_value,
            error=self.error
        )
        value = aggregator(**kwargs)
        uncertainty = qr_uncertainty(median=value if aggregator is qr_median else None, **kwargs)
        return Score(value, uncertainty, uncertainty)


    ############################################
    ##  Methods to esimate the multiplicators ##
    ############################################

    def compute_model_norms(self,
        users: Users,
        made_public: MadePublic, # key_names == ["username", "entity_name"]
        scores: MultiScore, # key_names == ["username", "entity_name"]
    ) -> dict[str, float]:
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
        out: dict[str, float]
            out[username] is the norm of user's score vector
        """
        return { str(user): self.compute_model_norm(made_public[user], scores[user]) for user in users }

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
    ) -> tuple[NestedDictOfRowLists, NestedDictOfRowLists]: # key_names == ["scalee_name", "scaler_name"]
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
        weight_lists: NestedDictOfRowLists
            With key_names == ["scalee_name", "scaler_name"]
            weight_lists[scalee_name, scaler_name] is a list of weights, for pairs
            of entities.
        ratio_lists: NestedDictOfRowLists
            With key_names == ["scalee_name", "scaler_name"]
            multiscore[scalee_name, scaler_name] is a list of ratios of score differences,
            each of which is of type Score.
        """
        reordered_scaler_scores = scaler_scores.reorder_keys(["entity_name", "username"])
        weight_lists, ratio_lists = NestedDictOfRowList(), NestedDictOfRowList()
        
        for scalee in scalees:
            scalee_entity_names = scalee_scores[scalee].get_set("entity_name")
            scalers = reordered_scaler_scores[scalee_entity_names].get_set("username")
        
            for scaler in scalers:
                
                if str(scalee) == str(scaler):
                    weight_lists[scalee, scaler] = 1
                    ratio_lists[scalee, scaler] = [Score(1, 0, 0)]
                    continue
                
                common_entity_names = scalee_entity_names & scaler_scores[scaler].get_set("entity_name")
                
                if len(common_entity_names) <= 1:
                    continue
                if len(common_entity_names) <= self.n_entity_to_fully_compare_max:
                    pairs = UnorderedPairs(common_entity_names)
                else:
                    pairs = UnorderedPairs(common_entity_names).n_samples(self.n_diffs_sample_max)
                
                weight_list, ratio_list = self.compute_ratios(
                    scalee_scores[scalee], 
                    scaler_scores[scaler], 
                    made_public[scaler],
                    pairs
                )
                if weight_list:
                    weight_lists[scalee, scaler] = weight_list
                    ratio_lists[scalee, scaler] = ratio_list

        return weight_lists, ratio_lists

    def compute_ratios(self,
        scalee_scores: MultiScore, # key_name == ["entity_name"]
        scaler_scores: MultiScore, # key_name == ["entity_name"]
        scaler_public: MadePublic, # key_name == ["entity_name"]
        pairs: Iterable # outputs list of pairs (e, f) of entity names
    ) -> tuple[list[float], list[Score]]:
        """ Returns the scaler's voting right and ratios to multiplicatively scale scalee's model """
        weight_list, ratio_list = 0, list()
        for e, f in pairs:
            ratio = (scaler_scores[e] - scaler_scores[f]) / (scalee_scores[e] - scalee_scores[f])
            if ratio.isnan(): continue
            ratio_list.append(ratio.abs())
            weight_list.append(self.penalty(scaler_public[e]) * self.penalty(scaler_public[f]))
        return weight_list, ratio_list

    def compute_multiplicators(self, 
        voting_rights: VotingRights, # key_names == ["scalee_name", "scaler_name"]
        ratios: MultiScore, # key_names == ["scalee_name", "scaler_name"]
        model_norms: dict[str, float]
    ) -> MultiScore: # key_names = ["scalee_name"]
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
        return MultiScore({
            scalee_name: self.aggregate_scalers(
                voting_rights[scalee_name], 
                ratios[scalee_name],
                self.lipschitz / (8 * (1e-9 + model_norms[scalee_name])), 
                default_value=1.0, 
                default_dev=self.default_multiplicator_dev
            ).to_triplet()
            for scalee_name in voting_rights.get_set("scalee_name")
        }, key_names=["scalee_name"])

    ############################################
    ##   Methods to esimate the translations  ##
    ############################################
    
    def compute_entity_diffs(self, 
        scalees: Users, 
        scalers: Users, 
        made_public: MadePublic, # key_names == ["username", "entity_name"]
        scalee_scores: MultiScore, # key_names == ["username", "entity_name"]
        scaler_scores: MultiScore, # key_names == ["username", "entity_name"]
    ) -> tuple[NestedDictOfRowLists, NestedDictOfRowLists]: # key_names == ["scalee_name", "scaler_name"]
        """ Computes the score differences on entities that both scaler and scalee evaluated.
        This corresponds to tau_{uve} in paper.
        
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
        weight_lists: NestedDictOfRowLists
            With key_names == ["scalee_name", "scaler_name"]
            weight_lists[scalee_name, scaler_name] is a list of weights for common entities
        diff_lists: NestedDictOfRowLists
            With key_names == ["scalee_name", "scaler_name"]
            diff_lists[user][user_bis] is a a list of score differences,
            of type Score (i.e. with left and right uncertainties).
        """
        reordered_scaler_scores = scaler_scores.reorder_keys(["entity_name", "username"])
        weight_lists, diff_lists = NestedDictOfRowList(), NestedDictOfRowList()
        
        for scalee in scalees:
            scalee_entity_names = scalee_scores[scalee].get_set("entity_name")
            scalers = reordered_scaler_scores[scalee_entity_names].get_set("username")
        
            for scaler in scalers:
                
                if str(scalee) == str(scaler):
                    weight_lists[scalee, scaler] = 1
                    diff_lists[scalee, scaler] = [Score(0, 0, 0)]
                    continue
                
                common_entity_names = scalee_entity_names & scaler_scores[scaler].get_set("entity_name")
                
                if len(common_entity_names) > 0:
                    diff_lists[scalee, scaler] = [
                        scaler_scores[scaler, entity_name] - scalee_scores[scalee, entity_name]
                        for entity_name in common_entity_names
                    ]
                    weight_lists[scalee, scaler] = [
                        self.penalty(made_public[scaler, entity_name])
                        for entity_name in common_entity_names
                    ]

        return weight_lists, ratio_lists

    def compute_translations(self, 
        voting_rights: VotingRights, # key_names == ["scalee_name", "scaler_name"]
        diffs: MultiScore, # key_names == ["scalee_name", "scaler_name"]
    ) -> MultiScore: # key_names = ["scalee_name"]
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
        return MultiScore({
            scalee_name: self.aggregate_scalers(
                voting_rights[scalee_name], 
                diffs[scalee_name],
                self.lipschitz / 8, 
                default_value=0.0, 
                default_dev=self.default_translation_dev
            ).to_triplet()
            for scalee_name in voting_rights.get_set("scalee_name")
        }, key_names=["scalee_name"])

