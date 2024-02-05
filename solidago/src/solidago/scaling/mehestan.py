import numpy as np
import pandas as pd

import logging
import timeit

from .base import Scaling

from solidago.privacy_settings import PrivacySettings
from solidago.scoring_model import ScoringModel, ScaledScoringModel
from solidago.voting_rights import VotingRights
from solidago.primitives import qr_median, qr_uncertainty, lipschitz_resilient_mean

logger = logging.getLogger(__name__)


class Mehestan(Scaling):
    def __init__(
        self, 
        lipschitz=0.1, 
        min_activity=10, 
        n_scalers_max=100, 
        privacy_penalty=0.5,
        user_comparison_lipschitz=10.0,
        p_norm_for_multiplicative_resilience=4.0,
        error=1e-5
    ):
        """ Mehestan performs Lipschitz-resilient ollaborative scaling.
        
        A simplified version of Mehestan was published in 
        "Robust Sparse Voting", Youssef Allouah, Rachid Guerraoui, Lȩ Nguyên Hoang
        and Oscar Villemaud, published at AISTATS 2024.
        
        The inclusion of uncertainties is further detailed in
        "Solidago: A Modular Pipeline for Collaborative Scoring"
        
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
        self.error = error
    
    def __call__(
        self, 
        user_models: dict[int, ScoringModel],
        users: pd.DataFrame,
        entities: pd.DataFrame,
        voting_rights: VotingRights = None,
        privacy: PrivacySettings = None
    ) -> dict[int, ScoringModel]:
        """ Returns scaled user models
        
        Parameters
        ----------
        user_models: dict[int, ScoringModel]
            user_models[user] is user's scoring model
        users: DataFrame with columns
            * user_id (int, index)
            * trust_score (float)
        entities: DataFrame with columns
            * entity_id (int, ind)
        voting_rights: VotingRights
            Not used in Mehestan
        privacy: PrivacySettings
            privacy[user, entity] in { True, False, None }

        Returns
        -------
        out[user]: ScoringModel
            Will be scaled by the Scaling method
        """
        logger.info("Starting Mehestan's collaborative scaling")
        
        start = timeit.default_timer()
        logger.info("Mehestan 1. Select scalers based on activity and trustworthiness")
        score_diffs = _compute_score_diffs(user_models, users, entities)
        end1a = timeit.default_timer()
        logger.info(f"    Mehestan 1a. Score diffs in {int(end1a - start)} seconds")
        activities = _compute_activities(score_diffs, users, privacy, self.privacy_penalty)
        end1b = timeit.default_timer()
        logger.info(f"    Mehestan 1b. Activities in {int(end1b - end1a)} seconds")
        users = users.assign(is_scaler=self.compute_scalers(activities, users))
        end1c = timeit.default_timer()
        logger.info(f"    Mehestan 1c. Scalers in {int(end1c - end1b)} seconds")
        scalers = users[users["is_scaler"]]
        nonscalers = users[users["is_scaler"] == False]
        if len(scalers) == 0:
            logger.warning("    No user qualifies as a scaler. No scaling performed.")
            return user_models
        end_step1 = timeit.default_timer()
        logger.info(f"Mehestan 1. Terminated in {int(end_step1 - start)} seconds")
        
        logger.info("Mehestan 2. Collaborative scaling of scalers")
        model_norms = _model_norms(user_models, entities, privacy, 
            power=self.p_norm_for_multiplicative_resilience,
            privacy_penalty=self.privacy_penalty
        )
        end2a = timeit.default_timer()
        logger.info(f"    Mehestan 2a. Model norms in {int(end2a - end_step1)} seconds")
        multiplicators, translations, scaled_models = self.scale_scalers(
            user_models, scalers, entities, score_diffs, model_norms)
        end_step2 = timeit.default_timer()
        logger.info(f"Mehestan 2. Terminated in {int(end_step2 - end_step1)} seconds")
        
        logger.info("Mehestan 3. Scaling of non-scalers")
        for scaler in scaled_models:
            score_diffs[scaler] = _compute_user_score_diffs(scaled_models[scaler], entities)
        end3a = timeit.default_timer()
        logger.info(f"    Mehestan 3a. Score diffs in {int(end3a - end_step2)} seconds")
        scaled_models = self.scale_non_scalers(
            user_models, scalers, nonscalers, entities, score_diffs, model_norms, 
            multiplicators, translations, scaled_models)
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
        
    def compute_scalers(self, activities: dict[int, float], users: pd.DataFrame) -> np.ndarray:
        """ Determines which users will be scalers.
        The set of scalers is restricted for two reasons.
        First, too inactive users are removed, because their lack of comparability
        with other users makes the scaling process ineffective.
        Second, scaling scalers is the most computationally demanding step of Mehestan.
        Reducing the number of scalers accelerates the computation.
        
        Parameters
        ----------
        activities: np.ndarray
            activities[user] is the activity of user, 
            weighted by their trustworthiness and how public their activity is
            
        Returns
        -------
        is_scaler: np.ndarray
            is_scaler[user]: bool says whether user is a scaler
        """
        index_to_user = { index: user for index, user in enumerate(users.index) }
        np_activities = np.array([
            activities[index_to_user[index]]
            for index in range(len(users))
        ])
        argsort = np.argsort(np_activities)
        is_scaler = np.array([False] * len(np_activities))
        for user in range(min(self.n_scalers_max, len(np_activities))):
            if np_activities[argsort[-user-1]] < self.min_activity:
                break
            is_scaler[argsort[-user-1]] = True
        return is_scaler
    
    def scale_scalers(self, user_models, scalers, entities, score_diffs, model_norms):
        end2a = timeit.default_timer()
        entity_ratios = self.compute_entity_ratios(scalers, scalers, score_diffs)
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
            user_models, scalers, scalers, entities, multiplicators
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
        
        return multiplicators, translations, { 
            u: ScaledScoringModel(
                base_model=user_models[u], 
                multiplicator=multiplicators[u][0], 
                translation=translations[u][0],
                multiplicator_left_uncertainty=multiplicators[u][1], 
                multiplicator_right_uncertainty=multiplicators[u][1], 
                translation_left_uncertainty=translations[u][1],
                translation_right_uncertainty=translations[u][1]
            ) for u in scalers.index
        }
        
    def scale_non_scalers(self, user_models, scalers, nonscalers, entities, 
            score_diffs, model_norms, multiplicators, translations, scaled_models):
        end3a = timeit.default_timer()
        entity_ratios = self.compute_entity_ratios(nonscalers, scalers, score_diffs)
        end3b = timeit.default_timer()
        logger.info(f"    Mehestan 3b. Entity ratios in {int(end3b - end3a)} seconds")
        ratio_voting_rights, ratios, ratio_uncertainties = _aggregate_user_comparisons(
            scalers, entity_ratios, error=self.error, lipschitz=self.user_comparison_lipschitz
        )
        end3c = timeit.default_timer()
        logger.info(f"    Mehestan 3c. Aggregate ratios in {int(end3c - end3b)} seconds")
        multiplicators |= self.compute_multiplicators(
            ratio_voting_rights, ratios, ratio_uncertainties, model_norms
        )
        end3d = timeit.default_timer()
        logger.info(f"    Mehestan 3d. Multiplicators in {int(end3d - end3c)} seconds")
        
        entity_diffs = self.compute_entity_diffs(
            user_models, nonscalers, scalers, entities, multiplicators)
        end3e = timeit.default_timer()
        logger.info(f"    Mehestan 3e. Entity diffs in {int(end3e - end3d)} seconds")
        diff_voting_rights, diffs, diff_uncertainties = _aggregate_user_comparisons(
            scalers, entity_diffs, error=self.error, lipschitz=self.user_comparison_lipschitz
        )
        end3f = timeit.default_timer()
        logger.info(f"    Mehestan 3f. Aggregate diffs in {int(end3f - end3e)} seconds")
        translations |= self.compute_translations(diff_voting_rights, diffs, diff_uncertainties)
        end3g = timeit.default_timer()
        logger.info(f"    Mehestan 3g. Translations in {int(end3g - end3f)} seconds")
        
        return scaled_models | { 
            u: ScaledScoringModel(
                base_model=user_models[u], 
                multiplicator=multiplicators[u][0], 
                translation=translations[u][0],
                multiplicator_left_uncertainty=multiplicators[u][1], 
                multiplicator_right_uncertainty=multiplicators[u][1], 
                translation_left_uncertainty=translations[u][1],
                translation_right_uncertainty=translations[u][1]
            ) for u in nonscalers.index
        }
        
    
    ############################################
    ##  Methods to esimate the multiplicators ##
    ############################################
    
    def compute_entity_ratios(
        self, 
        scalees: pd.DataFrame, 
        scalers: pd.DataFrame, 
        score_diffs: dict[int, dict[int, tuple[list[float], list[float], list[float]]]]
    ) -> dict[int, dict[int, tuple[list[float], list[float], list[float]]]]:
        """ Computes the ratios of score differences, with uncertainties,
        for comparable entities of any pair of scalers (s_{uvef} in paper),
        for u in scalees and v in scalers.
        Note that the output rations[u][v] is given as a 1-dimensional np.ndarray
        without any reference to e and f.
        
        Parameters
        ----------
        scalees: DataFrame with columns
            * user_id (int, index)
        scalers: DataFrame with columns
            * user_id (int, index)
        score_diffs: list[dict[int, dict[int, tuple[float, float, float]]]]
            score_diff, left, right = score_diffs[user][entity_a][entity_b]
            yields the score difference, along with the left and right uncertainties
        
        Returns
        -------
        out: dict[int, dict[int, tuple[list[float], list[float], list[float]]]]
            out[user][user_bis] is a tuple (ratios, lefts, rights),
            where ratios is a list of ratios of score differences,
            and left and right are the left and right ratio uncertainties.
        """
        user_entity_ratios = dict()
        
        for u in scalees.index:
            user_entity_ratios[u] = dict()
            if len(score_diffs[u]) == 0:
                continue
            
            for v in scalers.index:
                if u == v:
                    user_entity_ratios[u][v] = [1], [0], [0]
                    continue
                
                entities = list(set(score_diffs[u].keys()) & set(score_diffs[v].keys()))
                if len(entities) <= 1:
                    continue
                
                user_entity_ratios[u][v] = list(), list(), list()
                for e_index, e in enumerate(entities):
                    f_entities = set(entities[e_index + 1:]) 
                    f_entities &= set(score_diffs[u][e]) 
                    f_entities &= set(score_diffs[v][e])
                    for f in f_entities:
                        ratio = np.abs(score_diffs[v][e][f][0] / score_diffs[u][e][f][0])
                        user_entity_ratios[u][v][0].append(ratio)
                        user_entity_ratios[u][v][1].append(ratio - np.abs(
                            (score_diffs[v][e][f][0] - score_diffs[v][e][f][1])
                            / (score_diffs[u][e][f][0] + score_diffs[u][e][f][2])
                        ))
                        user_entity_ratios[u][v][2].append(np.abs(
                            (score_diffs[v][e][f][0] + score_diffs[v][e][f][2])
                            / (score_diffs[u][e][f][0] - score_diffs[u][e][f][1])
                        ) - ratio)

                if len(user_entity_ratios[u][v][0]) == 0:
                    del user_entity_ratios[u][v]
                
        return user_entity_ratios

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
                voting_rights[u] + [1.], ratios[u] + [1.], uncertainties[u] + [0.], 
                default_value=1, error=self.error)
            for u in voting_rights
        }
            
    ############################################
    ##   Methods to esimate the translations  ##
    ############################################
    
    def compute_entity_diffs(
        self, 
        user_models: dict[int, ScoringModel],
        scalees: pd.DataFrame, 
        scalers: pd.DataFrame, 
        entities: pd.DataFrame,
        multiplicators: dict[int, tuple[float, float]]
    ) -> dict[int, dict[int, tuple[list[float], list[float], list[float]]]]:
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
        
        for u in scalees.index:
            u_entities = user_models[u].scored_entities(entities)
            differences[u] = dict()
            for v in scalers.index:
                if u == v:
                    continue
                
                v_entities = user_models[v].scored_entities(entities)
                uv_entities = u_entities.intersection(v_entities)
                if len(uv_entities) == 0:
                    continue
                    
                differences[u][v] = list(), list(), list()                
                for e in uv_entities:
                    score_u, left_u, right_u = user_models[u](e, entities.loc[e])
                    score_v, left_v, right_v = user_models[v](e, entities.loc[e])
                    
                    differences[u][v][0].append(
                        multiplicators[v][0] * score_v 
                        - multiplicators[u][0] * score_u
                    )
                    differences[u][v][1].append(
                        multiplicators[u][0] * left_u
                        + multiplicators[u][1] * score_u * (score_u > 0)
                        - multiplicators[u][1] * score_u * (score_u < 0)
                        + multiplicators[v][0] * left_v
                        + multiplicators[v][1] * score_v * (score_v > 0)
                        - multiplicators[v][1] * score_v * (score_v < 0)
                    )
                    differences[u][v][2].append(
                        multiplicators[u][0] * right_u
                        - multiplicators[u][1] * score_u * (score_u < 0)
                        + multiplicators[u][1] * score_u * (score_u > 0)
                        + multiplicators[v][0] * right_v
                        - multiplicators[v][1] * score_v * (score_v < 0)
                        + multiplicators[v][1] * score_v * (score_v > 0)
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
                voting_rights[u] + [1.], diffs[u] + [0.], uncertainties[u] + [0.], 
                default_value=0, error=self.error, aggregator=lipschitz_resilient_mean)
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

def _compute_score_diffs(
    user_models: dict[int, ScoringModel],
    users: pd.DataFrame,
    entities: pd.DataFrame
) -> dict[int, dict[int, dict[int, tuple[float, float, float]]]]:
    """ Computes, for each user, the score difference 
    between pairs of judged entities (theta_{uef} in paper).
    
    Parameters
    ----------
    user_models: dict[int, ScoringModel]
        user_models[user] is user's scoring model
    users: DataFrame with columns
        * user_id (int, index)
    entities: DataFrame with columns
        * entity_id (int, ind)
        
    Returns
    -------
    score_diffs: dict[int, dict[int, dict[int, tuple[float, float, float]]]]
        score_diff, left, right = score_diffs[user][entity_a][entity_b]
        yields the score difference, along with the left and right uncertainties
    """
    return { user: _compute_user_score_diffs(user_models[user], entities) for user in users.index }

def _compute_user_score_diffs(
    user_model: ScoringModel, 
    entities: pd.DataFrame
) -> dict[int, dict[int, tuple[float, float, float]]]:
    user_score_diffs = dict()
    scored_entities = list(user_model.scored_entities(entities))
    for a in scored_entities:
        user_score_diffs[a] = dict()
        score_a, left_a, right_a = user_model(a, entities.loc[a])
        for b in scored_entities:
            if b == a:
                continue
            score_b, left_b, right_b = user_model(b, entities.loc[b])
            if score_a - score_b >=  2 * left_a + 2 * right_b:
                user_score_diffs[a][b] = (score_a - score_b, left_a + right_b, right_a + left_b)
            if score_b - score_a >= 2 * left_b + 2 * right_a:
                user_score_diffs[a][b] = (score_b - score_a, left_b + right_a, right_b + left_a)
    return user_score_diffs

def _compute_activities(
    score_diffs: dict[int, dict[int, dict[int, tuple[float, float, float]]]],
    users: pd.DataFrame,
    privacy: PrivacySettings,
    privacy_penalty: float
) -> dict[int, float]:
    """ Returns a dictionary, which maps users to their trustworthy activeness.
    
    Parameters
    ----------
    users: DataFrame with columns
        * user_id (int, index)
        * trust_score (float)
    privacy: PrivacySettings
        privacy[user, entity] in { True, False, None }
    privacy_penalty: float
        Penalty for privacy

    Returns
    -------
    activities: dict[int, float]
        activities[user] is a measure of user's trustworthy activeness.
    """
    return { 
        user: _computer_user_activities(user, score_diffs[user], users, privacy, privacy_penalty)
        for user in score_diffs 
    }

def _computer_user_activities(
    user: int,
    score_diffs: dict[int, dict[int, tuple[float, float, float]]],
    users: pd.DataFrame,
    privacy: PrivacySettings,
    privacy_penalty: float
) -> dict[int, float]:
    """ Returns a dictionary, which maps users to their trustworthy activeness.
    
    Parameters
    ----------
    user: int
    score_diffs: dict[int, dict[int, tuple[float, float, float]]]
        score_diffs[e][f] is a tuple (score, left_uncertainty, right_uncertainty)
    users: DataFrame with columns
        * user_id (int, index)
        * trust_score (float)
    privacy: PrivacySettings
        privacy[user, entity] in { True, False, None }
    privacy_penalty: float
        Penalty for privacy

    Returns
    -------
    activities: dict[int, float]
        activities[user] is a measure of user's trustworthy activeness.
    """
    results = 0
    for e in score_diffs:
        for f in score_diffs[e]:
            if f < e:
                continue
            added_quantity = 1
            if privacy is not None and privacy[user, e]:
                added_quantity *= privacy_penalty
            if privacy is not None and privacy[user, f]:
                added_quantity *= privacy_penalty
            if "trust_score" in users:
                added_quantity *= users.loc[user, "trust_score"]
            results += added_quantity
    return results

def _model_norms(
    user_models: dict[int, ScoringModel],
    entities: pd.DataFrame,
    privacy: PrivacySettings,
    power: float,
    privacy_penalty: float
) -> dict[int, float]:
    """ Estimator of the scale of scores of a user, with an emphasis on large scores.
    The estimator uses a L_power norm, and weighs scores, depending on public/private status.
    For each user u, it computes (sum_e w[ue] * score[u, e]**power / sum_e w[ue])**(1/power).
    
    Parameters
    ----------
    user_models: dict[int, ScoringModel]
        user_models[user] is user's scoring model
    users: DataFrame with columns
        * user_id (int, index)
    entities: DataFrame with columns
        * entity_id (int, ind)
    privacy: PrivacySettings
        privacy[user, entity] in { True, False, None }
    privacy_penalty: float
        Penalty for privacy

    Returns
    -------
    out: dict[int, float]
        out[user]
    """
    return {
        user: _user_model_norms(user, user_models[user], entities, privacy, power, privacy_penalty)
        for user in user_models
    }

def _user_model_norms(
    user: int,
    user_model: ScoringModel,
    entities: pd.DataFrame,
    privacy: PrivacySettings,
    power: float,
    privacy_penalty: float
) -> dict[int, float]:
    """ Estimator of the scale of scores of a user, with an emphasis on large scores.
    The estimator uses a L_power norm, and weighs scores, depending on public/private status.
    For each user u, it computes (sum_e w[ue] * score[u, e]**power / sum_e w[ue])**(1/power).
    
    Parameters
    ----------
    user_models: dict[int, ScoringModel]
        user_models[user] is user's scoring model
    users: DataFrame with columns
        * user_id (int, index)
    entities: DataFrame with columns
        * entity_id (int, ind)
    privacy: PrivacySettings
        privacy[user, entity] in { True, False, None }
    privacy_penalty: float
        Penalty for privacy

    Returns
    -------
    out: dict[int, float]
        out[user]
    """
    weight_sum, weighted_sum = 0, 0
    
    for entity in user_model.scored_entities(entities):
        output = user_model(entity, entities.loc[entity])
        if output is None:
            continue
        
        weight = 1
        if privacy is not None and privacy[user, entity]:
            weight *= privacy_penalty
        
        weight_sum += weight
        weighted_sum += weight * (output[0]**power)
    
    if weight_sum == 0:
        return 1
    
    return np.power(weighted_sum / weight_sum, 1 / power)

def _aggregate_user_comparisons(
    users: pd.DataFrame, 
    scaler_comparisons: dict[int, dict[int, tuple[list[float], list[float], list[float]]]],
    error: float=1e-5,
    lipschitz: float=1.0
) -> dict[int, tuple[list[float], list[float], list[float]]]:
    """ For any two pairs (scalee, scaler), aggregates their comparative data.
    Typically used to transform s_{uvef}'s into s_{uv}, and tau_{uve}'s into tau_{uv}.
    The reference to v is also lost in the process, as it is then irrelevant.
    
    Parameters
    ----------
    users: DataFrame with columns
        * user_id (int, index)
        * trust_score (float)
    scaler_comparisons: dict[int, dict[int, tuple[list[float], list[float], list[float]]]]
        scaler_comparisons[user][user_bis] is a tuple (values, lefts, rights).
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
                users.loc[v, "trust_score"] if "trust_score" in users else 1
            )
            comparisons[u].append(qr_median(
                lipschitz=lipschitz, 
                values=np.array(scaler_comparisons[u][v][0]),
                voting_rights=1.0, 
                left_uncertainties=np.array(scaler_comparisons[u][v][1]),
                right_uncertainties=np.array(scaler_comparisons[u][v][2]),
                error=error
            ))
            uncertainties[u].append(qr_uncertainty(
                lipschitz=lipschitz, 
                values=np.array(scaler_comparisons[u][v][0]),
                voting_rights=1.0, 
                left_uncertainties=np.array(scaler_comparisons[u][v][1]),
                right_uncertainties=np.array(scaler_comparisons[u][v][2]),
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
    aggregator: callable=qr_median
) -> dict[int, tuple[float, float]]:
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
        error=error,
        median=value
    )
    return value, uncertainty
