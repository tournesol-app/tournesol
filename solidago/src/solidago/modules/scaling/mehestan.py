from typing import Callable, Optional, Iterable
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np
import numpy.typing as npt
import pandas as pd
import logging

logger = logging.getLogger(__name__)

from solidago.primitives.lipschitz import qr_median, qr_uncertainty, lipschitz_resilient_mean
from solidago.primitives.datastructure.multi_key_table import MultiKeyTable
from solidago.primitives.pairs import UnorderedPairs
from solidago.primitives.timer import time
from solidago.state import *
from solidago.modules.base import StateFunction


class Mehestan(StateFunction):
    def __init__(self, 
        lipschitz: float=0.1, 
        min_scaler_activity: float=10.0,
        n_scalers_max: float=100, 
        privacy_penalty: float=0.5,
        user_comparison_lipschitz: float=10.0,
        p_norm_for_multiplicative_resilience: float=4.0,
        n_entity_to_fully_compare_max: float=100,
        n_diffs_sample_max: float=1000,
        default_multiplier_dev: float=0.5,
        default_translation_dev: float=1.,
        error: float=1e-5,
        *args, **kwargs,
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
            we enforce a large resilience on multiplier estimation,
            when the model scores of a user are large.
            The infinite norm may be to sensitive to extreme values,
            thus we propose to use an l_p norm.
        error: float
            Error bound
        """
        super().__init__(*args, **kwargs)
        self.lipschitz = lipschitz
        self.min_scaler_activity = min_scaler_activity
        self.n_scalers_max = n_scalers_max
        self.privacy_penalty = privacy_penalty
        self.user_comparison_lipschitz = user_comparison_lipschitz
        self.p_norm_for_multiplicative_resilience = p_norm_for_multiplicative_resilience
        self.n_entity_to_fully_compare_max = n_entity_to_fully_compare_max
        self.n_diffs_sample_max = n_diffs_sample_max
        self.default_multiplier_dev = default_multiplier_dev
        self.default_translation_dev = default_translation_dev
        self.error = error

    """ A simple way to distribute computations is to parallelize the loop of __call__ """
    def __call__(self, 
        users: Users,
        entities: Entities,
        made_public: MadePublic,
        user_models: UserModels,
    ) -> tuple[Users, UserModels]:
        """ Returns scaled user models.
        
        Returns
        -------
        users: Users
            Records whether users are Mehestan-scalers
        user_models: ScoringModel
            Scaled user models
        """
        logger.info("Starting Mehestan's collaborative scaling")
        assert "trust_score" in users.columns, "No trust scores. Consider running TrustAll first."

        scales = MultiScore(keynames=["username", "kind", "criterion"])
        scores = user_models(entities)
        fixed_args = users, entities, made_public
        args_list = [(c, scores.get(criterion=c)) for c in user_models.criteria()]
        results = list()
        with ThreadPoolExecutor(max_workers=self.max_workers) as e:
            futures = {e.submit(self.scale_criterion, *fixed_args, s): c for c, s in args_list}
            for f in as_completed(futures):
                results.append((futures[f], f.result()))
        for criterion, (subscales, activities, is_scaler) in results:
            scales |= subscales.prepend(criterion=criterion)
            users[f"activities_{criterion}"] = activities
            users[f"is_scaler_{criterion}"] = is_scaler
        return users, user_models.scale(scales, note="mehestan")

    def save_result(self, state: State, directory: Optional[str]=None) -> tuple[str, dict]:
        if directory is not None:
            state.users.save(directory)
            state.user_models.user_scales.save(directory, "user_scales.csv")
        with time(logger, "Saving state.json"):
            instructions = state.save_instructions(directory)
        return instructions
    
    def scale_criterion(self, 
        users: Users,
        entities: Entities,
        made_public: MadePublic, # keynames == ["username", "entity_name"]
        scores: MultiScore,
    ) -> tuple[MultiScore, npt.NDArray, npt.NDArray]: # scales, activies, is_scaler
        activities, is_scaler = self.compute_activities_and_scalers(users, made_public, scores)
        if not any(is_scaler):
            logger.warning("  No user qualifies as a scaler. No scaling performed.")
            return MultiScore(keynames=["username", "kind"]), activities, is_scaler
        scalers, nonscalers = set(), set()
        for index, user in enumerate(users):
            (scalers if is_scaler[index] else nonscalers).add(str(user))
        
        scaler_scores, nonscaler_scores = scores[scalers], scores[nonscalers]
        scale_scalers_to_scalers_args = (users, made_public, scaler_scores, scaler_scores, True)
        scaler_scales, scaler_scores = self.scale_to_scalers(*scale_scalers_to_scalers_args)

        scale_nonscalers_to_scalers_args = (users, made_public, scaler_scores, nonscaler_scores)
        nonscaler_scales, _ = self.scale_to_scalers(*scale_nonscalers_to_scalers_args)
        
        return (scaler_scales | nonscaler_scales), activities, is_scaler

    ############################################
    ##  The three main steps are              ##
    ##  1. Select the subset of scalers       ##
    ##  2. Scale the scalers                  ##
    ##  3. Fit the nonscalers to the scalers  ##
    ############################################

    def compute_activities_and_scalers(self,
        users: Users,
        made_public: MadePublic, # keynames == ["username", "entity_name"]
        scores: MultiScore, # keynames == ["username", "entity_name"]
    ) -> tuple[np.ndarray, np.ndarray]:
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
        activities = self.compute_activities(users, made_public, scores) # np.ndarray
        argsort = np.argsort(activities)
        is_scaler = np.array([False] * len(activities))
        for user_index in range(min(self.n_scalers_max, len(activities))):
            if activities[argsort[-user_index-1]] < self.min_scaler_activity:
                break
            is_scaler[argsort[-user_index-1]] = True
        return activities, is_scaler

    def scale_to_scalers(self, 
        users: Users,
        made_public: MadePublic, # keynames == ["username", "entity_name"]
        scaler_scores: MultiScore, # keynames == ["username", "entity_name"]
        scalee_scores: MultiScore, # keynames == ["username", "entity_name"]
        scalees_are_scalers: bool=False
    ) -> tuple[MultiScore, MultiScore]: # scalee_scales, scalee_scores
        s = "2" if scalees_are_scalers else "3"
        scalee_model_norms = self.compute_model_norms(made_public, scalee_scores)
    
        ratio_weight_lists, ratio_lists = self.ratios(made_public, scaler_scores, scalee_scores)
        ratio_args = users, ratio_weight_lists, ratio_lists, self.default_multiplier_dev
        voting_rights, ratios = self.aggregate_scaler_scores(*ratio_args)
        multipliers = self.compute_multipliers(voting_rights, ratios, scalee_model_norms)
        for (scalee_name, entity_name), score in scalee_scores:
            scalee_scores[scalee_name, entity_name] = score * multipliers[scalee_name]
        if scalees_are_scalers:
            scaler_scores = scalee_scores
    
        diff_weight_lists, diff_lists = self.diffs(made_public, scaler_scores, scalee_scores)
        diff_args = users, diff_weight_lists, diff_lists, self.default_translation_dev
        voting_rights, diffs = self.aggregate_scaler_scores(*diff_args)
        translations = self.compute_translations(voting_rights, diffs)
        for (scalee_name, entity_name), score in scalee_scores:
            scalee_scores[scalee_name, entity_name] = score + translations[scalee_name]
    
        multipliers = multipliers.prepend(kind="multiplier")
        translations = translations.prepend(kind="translation")
        return (multipliers | translations), scalee_scores

    ############################################
    ##    Methods to estimate the scalers     ##
    ############################################

    def compute_activities(self,
        users: Users, 
        made_public: MadePublic, # keynames == ["username", "entity_name"]
        scores: MultiScore, # keynames == ["username", "entity_name"]
    ) -> np.ndarray:
        """ Returns a dictionary, which maps users to their trustworthy activeness.
        
        Parameters
        ----------
        users: Users
        made_public: MadePublic
            Must have keynames "username" and "entity_name"
        scores: MultiScore
            Must have keynames == ["username", "entity_name"]
    
        Returns
        -------
        activities: np.ndarray
            activities[i] is a measure of user i's trustworthy activeness,
            where i is the iloc of the user in users
        """
        return np.array([
            self.compute_user_activities(float(user["trust_score"]), made_public[user], scores[user])
            for user in users
        ])
    
    def compute_user_activities(self,
        trust: float,
        made_public: MadePublic, # keynames = ["entity_name"]
        scores: MultiScore, # keynames = ["entity_name"]
    ) -> float:
        """ Returns a dictionary, which maps users to their trustworthy activeness.
        
        Parameters
        ----------
        made_public: MadePublic with keynames = ["entity_name"]
        scores: MultiScore with keynames = ["entity_name"]
    
        Returns
        -------
        activity: float
        """
        if trust <= 0.0:
            return 0.0
        
        sum_of_activities = sum([
            made_public.penalty(self.privacy_penalty, entity_name)
            for (entity_name,), score in scores if not (0 in score)
        ])
        
        return trust * sum_of_activities

    #############################################################
    ##  Methods used for both multipliers and translations  ##
    #############################################################

    def scaler_scalee_comparison_lists(self, 
        made_public: MadePublic, # keynames == ["username", "entity_name"]
        scalers_scores: MultiScore, # keynames == ["username", "entity_name"]
        scalees_scores: MultiScore, # keynames == ["username", "entity_name"]
        compute_scaler_scalee_comparisons: Callable,
        default_value: Score,
    ) -> tuple[defaultdict, defaultdict]: # keynames == ["scalee_name", "scaler_name"]
        """ Computes the comparisons of scores, with uncertainties,
        for comparable entities of any pair of scalers (x_{uvef} in paper) (for x=s or tau),
        for u in scalees and v in scalers.
        
        Parameters
        ----------
        made_public: MadePublic
            Must have keynames == ["username", "entity_name"]
        scalee_scores: MultiScore
            Must have keynames == ["username", "entity_name"]
        scaler_scores: MultiScore
            Must have keynames == ["username", "entity_name"]
        
        Returns
        -------
        weight_lists: VotingRights
            With keynames == ["scalee_name", "scaler_name"] and last_only == False
            weight_lists.get(scalee_name, scaler_name) is a list of weights, for pairs
            of entities.
        comparison_lists: MultiScore
            With keynames == ["scalee_name", "scaler_name"] and last_only == False
            multiscore.get(scalee_name, scaler_name) is a list of comparisons of score differences,
            each of which is of type Score.
        """
        weight_lists = defaultdict(lambda: defaultdict(list))
        comparison_lists = defaultdict(lambda: defaultdict(list))
        
        for scalee_name in scalees_scores.keys("username"):
            scalee_scores = scalees_scores[scalee_name] # keynames == ["entity_name"]
            entity_names = scalee_scores.keys("entity_name")
            entity_scaler_scorers = lambda e: scalers_scores.get(entity_name=e).keys("username")
            
            for scaler_name in set.union(*[entity_scaler_scorers(e) for e in entity_names]):
                
                if scalee_name == scaler_name:
                    weight_lists[scalee_name][scaler_name] = [1.0]
                    comparison_lists[scalee_name][scaler_name] = [default_value]
                    continue
                
                scaler_scores = scalers_scores[scaler_name] # keynames == ["entity_name"]
                common_entity_names = entity_names & scaler_scores.keys("entity_name")
                args = (scalee_scores, scaler_scores, made_public[scaler_name], common_entity_names)
                output = compute_scaler_scalee_comparisons(self, *args)
                for weight, scaler_scalee_comparison in zip(*output):
                    weight_lists[scalee_name][scaler_name] += [weight]
                    comparison_lists[scalee_name][scaler_name] += [scaler_scalee_comparison]

        return weight_lists, comparison_lists
    
    def aggregate_scaler_scores(self,
        users: Users,
        weight_lists: defaultdict, # keynames == ["scalee_name", "scaler_name"], value_cls == list
        score_lists: defaultdict, # keynames == ["scalee_name", "scaler_name"], value_cls == list
        default_dev: float,
    ) -> tuple[VotingRights, MultiScore]: # keynames == ["scalee_name", "scaler_name"]
        """ For any two pairs (scalee, scaler), aggregates their ratio or diff data.
        Typically used to transform s_{uvef}'s into s_{uv}, and tau_{uve}'s into tau_{uv}.
        The reference to v is also lost in the process, as it is then irrelevant.
        
        Parameters
        ----------
        users: Users
        weight_lists: defaultdict(lambda: defaultdict(list))
        score_lists: defaultdict(lambda: defaultdict(list))
            
        Returns
        -------
        voting_rights: VotingRights
            With keynames == ["scalee_name", "scaler_name"]
        multiscores: MultiScore
            With keynames == ["scalee_name", "scaler_name"]
        """
        voting_rights = VotingRights(keynames=["scalee_name", "scaler_name"])
        multiscores = MultiScore(keynames=["scalee_name", "scaler_name"])
        
        common_kwargs = dict(lipschitz=self.user_comparison_lipschitz, error=self.error)
        for scalee_name in score_lists:
            for scaler_name, score_list in score_lists[scalee_name].items():
                kwargs = common_kwargs | dict(
                    values=np.array([s.value for s in score_list], dtype=np.float64),
                    voting_rights=np.array(weight_lists[scalee_name][scaler_name], dtype=np.float64),
                    left_uncertainties=np.array([s.left_unc for s in score_list], dtype=np.float64),
                    right_uncertainties=np.array([s.right_unc for s in score_list], dtype=np.float64),
                )
                value = qr_median(**kwargs)
                uncertainty = qr_uncertainty(median=value, default_dev=default_dev, **kwargs)
                multiscores[scalee_name, scaler_name] = Score(value, uncertainty, uncertainty)
                voting_rights[scalee_name, scaler_name] = users.get(scaler_name)["trust_score"]
                
        return voting_rights, multiscores

    def aggregate_scalers(self,
        voting_rights: VotingRights, # keynames = ["scaler_name"]
        scores: MultiScore, # keynames = ["scaler_name"]
        lipschitz: float,
        default_value: float, 
        default_dev: float, 
        aggregator: Callable = qr_median,
    ) -> Score:
        """ Computes the multipliers of users with given user_ratios
        
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
        multipliers: dict[int, tuple[float, float]]
            multipliers[user][0] is the multiplicative scaling of user
            multipliers[user][1] is the uncertainty on the multiplier
        """
        kwargs = dict(
            lipschitz=lipschitz, 
            voting_rights=np.array(voting_rights.values(), dtype=np.float64),
            values=np.array([s.value for _, s in scores], dtype=np.float64),
            left_uncertainties=np.array([s.left_unc for _, s in scores], dtype=np.float64),
            right_uncertainties=np.array([s.right_unc for _, s in scores], dtype=np.float64),
            error=self.error
        )
        value = aggregator(default_value=default_value, **kwargs)
        uncertainty = qr_uncertainty(median=value if aggregator is qr_median else None, **kwargs)
        return Score(value, uncertainty, uncertainty)


    ############################################
    ##  Methods to esimate the multipliers ##
    ############################################

    def compute_model_norms(self,
        made_public: MadePublic, # keynames == ["username", "entity_name"]
        scores: MultiScore, # keynames == ["username", "entity_name"]
    ) -> dict[str, float]:
        """ Estimator of the scale of scores of a user, with an emphasis on large scores.
        The estimator uses a L_power norm, and weighs scores, depending on public/private status.
        For each user u, it computes (sum_e w[ue] * score[u, e]**power / sum_e w[ue])**(1/power).
        
        Parameters
        ----------
        users: Users
        made_public: MadePublic
            Must have keynames == ["username", "entity_name"]
        scores: MultiScore
            Must have keynames == ["username", "entity_name"]
    
        Returns
        -------
        out: dict[str, float]
            out[username] is the norm of user's score vector
        """
        return { 
            username: self.compute_model_norm(made_public[username], scores[username]) 
            for username in scores.keys("username")
        }

    def compute_model_norm(self, made_public: MadePublic, scores: MultiScore) -> float:
        """ Estimator of the scale of scores of a user, with an emphasis on large scores.
        The estimator uses a L_power norm, and weighs scores, depending on public/private status.
        For each user u, it computes (sum_e w[ue] * score[u, e]**power / sum_e w[ue])**(1/power).
        
        Parameters
        ----------
        made_public: MadePublic
            Must have keynames == ["entity_name"]
        scores: MultiScore
            Must have keynames == ["entity_name"]
    
        Returns
        -------
        norm: float
        """
        weight_sum, weighted_sum = 0., 0.
        for entity_name, score in scores:
            weight = made_public.penalty(self.privacy_penalty, entity_name)
            weight_sum += weight
            weighted_sum += weight * (score.value**self.p_norm_for_multiplicative_resilience)
    
        if weight_sum == 0:
            return 1.0
    
        return np.power(weighted_sum / weight_sum, 1 / self.p_norm_for_multiplicative_resilience)

    def ratios(self, 
        made_public: MadePublic, # keynames == ["username", "entity_name"]
        scaler_scores: MultiScore, # keynames == ["username", "entity_name"]
        scalee_scores: MultiScore, # keynames == ["username", "entity_name"]
    ) -> tuple[defaultdict, defaultdict]: # keynames == ["scalee_name", "scaler_name"]
        """ Computes the ratios of score differences, with uncertainties,
        for comparable entities of any pair of scalers (s_{uvef} in paper),
        for u in scalees and v in scalers.
        
        Parameters
        ----------
        made_public: MadePublic
            Must have keynames == ["username", "entity_name"]
        scalee_scores: MultiScore
            Must have keynames == ["username", "entity_name"]
        scaler_scores: MultiScore
            Must have keynames == ["username", "entity_name"]
        
        Returns
        -------
        weight_lists: VotingRights
            With keynames == ["scalee_name", "scaler_name"] and last_only == False
            weight_lists.get(scalee_name, scaler_name) is a list of weights, for pairs
            of entities.
        ratio_lists: MultiScore
            With keynames == ["scalee_name", "scaler_name"] and last_only == False
            multiscore.get(scalee_name, scaler_name) is a list of ratios of score differences,
            each of which is of type Score.
        """
        args = (made_public, scaler_scores, scalee_scores, Mehestan.compute_ratios, Score(1, 0, 0))
        return self.scaler_scalee_comparison_lists(*args)

    def compute_ratios(self,
        scalee_scores: MultiScore, # key_name == ["entity_name"]
        scaler_scores: MultiScore, # key_name == ["entity_name"]
        scaler_public: MadePublic, # key_name == ["entity_name"]
        common_entity_names: set[str],
    ) -> tuple[list[float], list[Score]]:
        """ Returns the scaler's voting right and ratios to multiplicatively scale scalee's model """
        if len(common_entity_names) <= 1:
            return list(), list()
        pairs = UnorderedPairs(common_entity_names)
        if len(common_entity_names) > self.n_entity_to_fully_compare_max:
            pairs = pairs.n_samples(self.n_diffs_sample_max)
        weight_list, ratio_list = list(), list()
        penalty = lambda entity_name: scaler_public.penalty(self.privacy_penalty, entity_name)
        for e, f in pairs:
            ratio = (scaler_scores[e] - scaler_scores[f]) / (scalee_scores[e] - scalee_scores[f])
            if ratio.isnan(): continue
            ratio_list.append(ratio.abs())
            weight_list.append(penalty(e) * penalty(f))
        return weight_list, ratio_list

    def compute_multipliers(self, 
        voting_rights: VotingRights, # keynames == ["scalee_name", "scaler_name"]
        ratios: MultiScore, # keynames == ["scalee_name", "scaler_name"]
        model_norms: dict[str, float]
    ) -> MultiScore: # keynames = ["username"]
        """ Computes the multipliers of users with given user_ratios """
        kwargs = dict(default_value=1.0, default_dev=self.default_multiplier_dev)
        l = lambda scalee_name: self.lipschitz / (8 * (1e-9 + model_norms[scalee_name]))
        r = lambda scalee_name: ratios.get(scalee_name=scalee_name)
        return MultiScore(["username"], {
            (name,): self.aggregate_scalers(weights, r(name), l(name), **kwargs)
            for (name,), weights in voting_rights.iter("scalee_name")
        })

    ############################################
    ##   Methods to esimate the translations  ##
    ############################################
    
    def diffs(self, 
        made_public: MadePublic, # keynames == ["username", "entity_name"]
        scaler_scores: MultiScore, # keynames == ["username", "entity_name"]
        scalee_scores: MultiScore, # keynames == ["username", "entity_name"]
    ) -> tuple[defaultdict, defaultdict]: # keynames == ["scalee_name", "scaler_name"]
        """ Computes the score differences on entities that both scaler and scalee evaluated.
        This corresponds to tau_{uve} in paper.
        
        Parameters
        ----------
        scalees: Users, 
        scalers: Users, 
        made_public: MadePublic
            Must have keynames == ["username", "entity_name"]
        scalee_scores: MultiScore
            Must have keynames == ["username", "entity_name"]
        scaler_scores: MultiScore
            Must have keynames == ["username", "entity_name"]
        
        Returns
        -------
        weight_lists: VotingRights
            With keynames == ["scalee_name", "scaler_name"], last_only == True
            weight_lists[scalee_name, scaler_name] is a list of weights for common entities
        diff_lists: MultiScore
            With keynames == ["scalee_name", "scaler_name"], last_only == True
            diff_lists[user][user_bis] is a a list of score differences,
            of type Score (i.e. with left and right uncertainties).
        """
        args = (made_public, scaler_scores, scalee_scores, Mehestan.compute_diffs, Score(0, 0, 0))
        return self.scaler_scalee_comparison_lists(*args)

    def compute_diffs(self,
        scalee_scores: MultiScore, # key_name == ["entity_name"]
        scaler_scores: MultiScore, # key_name == ["entity_name"]
        scaler_public: MadePublic, # key_name == ["entity_name"]
        common_entity_names: set[str],
    ) -> tuple[list[float], list[Score]]:
        """ Returns the scaler's voting right and ratios to multiplicatively scale scalee's model """
        weight_list, diff_list = list(), list()
        penalty = lambda entity_name: scaler_public.penalty(self.privacy_penalty, entity_name)
        for entity_name in common_entity_names:
            diff_list.append(scaler_scores[entity_name] - scalee_scores[entity_name])
            weight_list.append(scaler_public.penalty(self.privacy_penalty, entity_name))
        return weight_list, diff_list

    def compute_translations(self, 
        voting_rights: VotingRights, # keynames == ["scalee_name", "scaler_name"]
        diffs: MultiScore, # keynames == ["scalee_name", "scaler_name"]
    ) -> MultiScore: # keynames = ["scalee_name"]
        """ Computes the multipliers of users with given user_ratios
        
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
            translations[user][1] is the uncertainty on the multiplier
        """
        kwargs = dict(
            lipschitz=self.lipschitz / 8, 
            default_value=0.0, 
            default_dev=self.default_translation_dev
        )
        return MultiScore(["username"], {
            name: self.aggregate_scalers(weights, diffs.get(name), **kwargs)
            for name, weights in voting_rights.iter("scalee_name")
        })

