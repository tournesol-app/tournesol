import numpy as np
import pandas as pd

import logging

from . import Scaling

from solidago.privacy_settings import PrivacySettings
from solidago.scoring_model import ScoringModel
from solidago.voting_rights import VotingRights
from solidago.primitives import qr_median, qr_uncertainty, br_mean

logger = logging.getLogger(__name__)


class Mehestan(Scaling):
    def __init__(
        self, 
        lipschitz=0.1, 
        min_n_judged_entities=10, 
        n_scalers_max=100, 
        privacy_penalty=0.5,
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
        self.min_n_judged_entities = min_n_judged_entities
        self.n_scalers_max = n_scalers_max
        self.privacy_penalty = privacy_penalty
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
        
        logger.info("Mehestan 1. Select scalers based on activity and trustworthiness")
        activities = _compute_activities(user_models, users, entities, privacy)
        users.assign(is_scaler=self.compute_scalers(activities))
        scalers = users[users["is_scaler"]]
        nonscalers = users[not users["is_scaler"]]
        
        logger.info("Mehestan 2. Collaborative scaling of scalers")
        model_norms = _model_norms(user_models, users, entities, privacy, 
            power=self.p_norm_for_multiplicative_resilience)
        score_diffs = _compute_score_diffs(user_models, scalers, entities)
        scaled_models = self.scale_scalers(user_models, scalers, entities, 
            score_diffs, model_norms)
        
        logger.info("Mehestan 3. Scaling of non-scalers")
        for scaler in scaled_models:
            user_models[scaler] = scaled_models[scaler]
        score_diffs = _compute_score_diffs(user_models, users, entities)
        scaled_models |= self.scale_non_scalers(user_models, nonscalers, entities, 
            score_diffs, model_norms, scaled_models)
        
        return scaled_models
    
    ############################################
    ##  The three main steps are              ##
    ##  1. Select the subset of scalers       ##
    ##  2. Scale the scalers                  ##
    ##  3. Fit the nonscalers to the scalers  ##
    ############################################
        
    def compute_scalers(self, n_judged_entities: np.ndarray) -> np.ndarray:
        """ Determines which users will be scalers.
        The set of scalers is restricted for two reasons.
        First, too inactive users are removed, because their lack of comparability
        with other users makes the scaling process ineffective.
        Second, scaling scalers is the most computationally demanding step of Mehestan.
        Reducing the number of scalers accelerates the computation.
        
        Parameters
        ----------
        n_judged_entities: np.ndarray
            n_judged_entities[user] is the number of entities judged by user
            
        Returns
        -------
        is_scaler: np.ndarray
            is_scaler[user]: bool says whether user is a scaler
        """
        argsort = np.argsort(n_judged_entities)
        is_scaler = np.array([False] * len(n_judged_entities))
        for user in range(min(self.n_scalers_max, len(n_judged_entities))):
            if n_judged_entities[argsort[-user]] < self.min_n_judged_entities:
                break
            is_scaler[argsort[-user]] = True
        return is_scaler
    
    def scale_scalers(self, user_models, scalers, entities, score_diffs, model_norms):
        entity_ratios = self.compute_entity_ratios(scalers, scalers, score_diffs)
        ratios = _aggregate_user_comparisons(scalers, entity_ratios, error=self.error)
        multiplicators = self.compute_multiplicators(ratios, model_norms)
        
        entity_diffs = self.compute_entity_diffs(
            user_models, scalers, scalers, entities, multiplicators)
        diffs = _aggregate_user_comparisons(scalers, entity_diffs, error=self.error)
        translations = self.compute_translations(diffs)
        
        return { 
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
        
    def scale_non_scalers(self, user_models, nonscalers, entities, 
            voting_rights, scaler_models, pairs):
        entity_ratios = self.compute_entity_ratios(nonscalers, scalers, score_diffs)
        ratios = _aggregate_user_comparisons(scalers, entity_ratios, error=self.error)
        multiplicators = self.compute_multiplicators(ratios, model_norms)
        
        entity_diffs = self.compute_entity_diffs(
            user_models, nonscalers, scalers, entities, multiplicators)
        diffs = _aggregate_user_comparisons(scalers, entity_diffs, error=self.error)
        translations = self.compute_translations(diffs)
        
        return { 
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
        
        raise NotImplementedError
        
    
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
            for v in scalers.index:
                if u == v:
                    continue
                
                entities = list(set(score_diffs[u].keys()) | set(score_diffs[v].keys()))
                if len(entities) <= 1:
                    continue
                    
                user_entity_ratios[u][v] = list(), list(), list()                
                for e_index, e in enumerate(entities):
                    for f in list(entities)[e_index + 1:]:
                        
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
                
        return user_entity_ratios

    def compute_multiplicators(
        self, 
        ratios: dict[int, tuple[list[float], list[float], list[float]]], 
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
            u: _aggregate(self.lipschitz / (8 / model_norms[u]), ratios[u], self.error)
            for u in ratios
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
                
                uv_entities = u_entities | user_models[v].scored_entities(entities)
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
                        + multiplicators[u][2] * score_u * (score_u < 0)
                        + multiplicators[v][0] * left_v
                        + multiplicators[v][1] * score_v * (score_v > 0)
                        + multiplicators[v][2] * score_v * (score_v < 0)
                    )
                    differences[u][v][2].append(
                        multiplicators[u][0] * right_u
                        + multiplicators[u][1] * score_u * (score_u < 0)
                        + multiplicators[u][2] * score_u * (score_u > 0)
                        + multiplicators[v][0] * right_v
                        + multiplicators[v][1] * score_v * (score_v < 0)
                        + multiplicators[v][2] * score_v * (score_v > 0)
                    )
                                    
        return differences

    def compute_translations(
        self, 
        diffs: dict[int, tuple[list[float], list[float], list[float]]]
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
            u: _aggregate(self.lipschitz / 8, diffs[u], self.error, br_mean)
            for u in diffs
        }    
    
##############################################
## Preprocessing to facilitate computations ##
##############################################
    
def _compute_activities(
    user_models: dict[int, ScoringModel],
    users: pd.DataFrame,
    entities: pd.DataFrame,
    privacy: PrivacySettings
) -> dict[int, float]:
    """ Returns a dictionary, which maps users to their trustworthy activeness.
    
    Parameters
    ----------
    user_models: dict[int, ScoringModel]
        user_models[user] is user's scoring model
    users: DataFrame with columns
        * user_id (int, index)
        * trust_score (float)
    entities: DataFrame with columns
        * entity_id (int, ind)
    privacy: PrivacySettings
        privacy[user, entity] in { True, False, None }

    Returns
    -------
    activities: dict[int, float]
        activities[user] is a measure of user's trustworthy activeness.
    """
    results = dict()
    for user in user_models:
        results[user] = 0
        scored_entities = user_models.scored_entities(entities)
        for entity in scored_entities:
            output = user_models[user](entity, entities.loc[entity])
            if output is None:
                continue
            added_quantity = 1
            if privacy is not None and privacy[user, entity]:
                added_quantity *= self.privacy_penalty
            elif "trust_score" in users:
                added_quantity *= users.loc[user, "trust_score"]
            results[user] += added_quantity
            
    return results
    
def _model_norms(
    user_models: dict[int, ScoringModel],
    users: pd.DataFrame,
    entities: pd.DataFrame,
    privacy: PrivacySettings,
    power: float=5.0
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

    Returns
    -------
    out: dict[int, float]
        out[user]
    """
    results = dict()
    for user in user_models:
        scored_entities = user_models.scored_entities(entities)
        weight_sum, weighted_sum = 0, 0
        for entity in scored_entities:
            output = user_models[user](entity, entities.loc[entity])
            if output is None:
                continue
            
            weight = 1
            if privacy is not None and privacy[user, entity]:
                weight *= self.privacy_penalty
            
            weight_sum += weight
            weighted_sum += weight * (output[0]**power)
                            
        results[user] = np.power(weighted_sum / weight_sum, 1 / power)
            
    return results       
    
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
    score_diffs = dict()
    for user in user_models.index:
        score_diffs[user] = dict()
        scored_entities = user_models.scored_entities(entities)
        for index, a in enumerate(scored_entities):
            for b in scored_entities[index + 1:]:
                score_a, left_a, right_a = user_models[user](a, entities.loc[a])
                score_b, left_b, right_b = user_models[user](b, entities.loc[b])
                if score_a - score_b >=  2 * left_a + 2 * right_b:
                    if a not in score_diffs[user]:
                        score_diffs[user][a] = dict()
                    score_diffs[user][a][b] = (
                        score_a - score_b, 
                        score_a - score_b - left_a - right_b,
                        score_a - score_b + right_a + left_b
                    )
                if score_b - score_a >= 2 * left_b + 2 * right_a:
                    if a not in score_diffs[user]:
                        score_diffs[user][a] = dict()
                    score_diffs[user][a][b] = (
                        score_b - score_a, 
                        score_b - score_a - left_b - right_a,
                        score_b - score_a + right_b + left_a
                    )
    return score_diffs
    
def _aggregate_user_comparisons(
    users: pd.DataFrame, 
    scaler_comparisons: dict[int, dict[int, tuple[list[float], list[float], list[float]]]],
    error: float=1e-5
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
    out: dict[int, tuple[list[float], list[float], list[float]]]
        out[u][0] is a list of voting rights
        out[u][1] is a list of values
        out[u][2] is a list of (symmetric) uncertainties
    """
    results = dict()
    
    for u in scaler_comparisons:
        results[u] = list(), list(), list()
        for v in scaler_comparisons[u]:
                            
            results[u][0].append(
                users.loc[v, "trust_score"] if "trust_score" in users else 1
            )
            results[u][1].append(qr_median(
                lipschitz=1, 
                values=np.array(scaler_comparisons[u][v][0]),
                voting_rights=1, 
                left_uncertainties=np.array(scaler_comparisons[u][v][1]),
                right_uncertainties=np.array(scaler_comparisons[u][v][2]),
                error=error
            ))
            results[u][2].append(qr_uncertainty(
                lipschitz=1, 
                values=np.array(scaler_comparisons[u][v][0]),
                voting_rights=1, 
                left_uncertainties=np.array(scaler_comparisons[u][v][1]),
                right_uncertainties=np.array(scaler_comparisons[u][v][2]),
                default_uncertainty=1,
                error=error,
                median=results[u][0][-1]
            ))
            
    return results
        
def _aggregate(
    lipschitz: float,
    values: dict[int, tuple[list[float], list[float], list[float]]], 
    error: float=1e-5,
    aggregator: callable=qr_median
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
    value = aggregator(
        lipschitz=lipschitz, 
        values=np.array(values[0]),
        voting_rights=np.array(values[u][1]), 
        left_uncertainties=np.array(values[u][2]),
        right_uncertainties=np.array(values[u][2]),
        error=error
    )
    uncertainty = qr_uncertainty(
        lipschitz=lipschitz, 
        values=np.array(values[1]),
        voting_rights=np.array(values[0]), 
        left_uncertainties=np.array(values[2]),
        right_uncertainties=np.array(values[2]),
        error=error,
        median=value
    )
    return value, uncertainty
