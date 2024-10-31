from typing import Callable, Mapping, Optional

import numpy as np
import pandas as pd

import logging
import timeit

from .base import Scaling
from .no_scaling import NoScaling

from solidago.privacy_settings import PrivacySettings
from solidago.scoring_model import ScoringModel, ScaledScoringModel
from solidago.voting_rights import VotingRights
from solidago.primitives import qr_median, qr_uncertainty, lipschitz_resilient_mean

from solidago.utils.pairs import UnorderedPairs


logger = logging.getLogger(__name__)


class Mehestan(Scaling):
    def __init__(
        self, 
        lipschitz=0.1, 
        min_activity=10.0,
        n_scalers_max=100, 
        privacy_penalty=0.5,
        user_comparison_lipschitz=10.0,
        p_norm_for_multiplicative_resilience=4.0,
        n_diffs_sample_max=1000,
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
        self.n_diffs_sample_max = n_diffs_sample_max
        self.error = error

    def __call__(
        self, 
        user_models: Mapping[int, ScoringModel],
        users: pd.DataFrame,
        entities: pd.DataFrame,
        voting_rights: Optional[VotingRights] = None,
        privacy: Optional[PrivacySettings] = None
    ) -> dict[int, ScaledScoringModel]:
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
        users = users.assign(is_scaler=self.compute_scalers(user_models, entities, users, privacy))
        scalers = users[users["is_scaler"]]
        nonscalers = users[users["is_scaler"] == False]
        if len(scalers) == 0:
            logger.warning("    No user qualifies as a scaler. No scaling performed.")
            return NoScaling()(user_models)
        end_step1 = timeit.default_timer()
        logger.info(f"Mehestan 1. Terminated in {int(end_step1 - start)} seconds")

        logger.info("Mehestan 2. Collaborative scaling of scalers")
        scaler_user_models = {u: m for u,m in user_models.items() if u in scalers.index}
        scaled_models = self.scale_scalers(scaler_user_models, scalers, entities, privacy)
        end_step2 = timeit.default_timer()
        logger.info(f"Mehestan 2. Terminated in {int(end_step2 - end_step1)} seconds")

        logger.info("Mehestan 3. Scaling of non-scalers")
        scaled_models = self.scale_non_scalers(user_models, nonscalers, entities, scalers, 
            scaled_models, privacy)
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

    def compute_scalers(
        self,
        user_models: Mapping[int, ScoringModel],
        entities: pd.DataFrame,
        users: pd.DataFrame,
        privacy: Optional[PrivacySettings],
    ) -> np.ndarray:
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
        activities = self.compute_activities(user_models, entities, users, privacy)
        index_to_user = { index: user for index, user in enumerate(users.index) }
        np_activities = np.array([
            activities.get(index_to_user[index], 0.0)
            for index in range(len(users))
        ])
        argsort = np.argsort(np_activities)
        is_scaler = np.array([False] * len(np_activities))
        for user in range(min(self.n_scalers_max, len(np_activities))):
            if np_activities[argsort[-user-1]] < self.min_activity:
                break
            is_scaler[argsort[-user-1]] = True
        return is_scaler

    def scale_scalers(self, user_models, scalers, entities, privacy):
        start = timeit.default_timer()
        model_norms = self.compute_model_norms(user_models, scalers, entities, privacy)
        end2a = timeit.default_timer()
        logger.info(f"    Mehestan 2a. Model norms in {int(end2a - start)} seconds")

        entity_ratios = self.compute_entity_ratios(user_models, user_models, entities, privacy)
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

    def compute_activities(
        self,
        user_models: Mapping[int, ScoringModel],
        entities: pd.DataFrame,
        users: pd.DataFrame,
        privacy: Optional[PrivacySettings],
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
            user_id: _computer_user_activities(
                user_id,  # type: ignore
                user_models[user_id],  # type: ignore
                entities,
                trust_score,  # type: ignore
                privacy,
                self.privacy_penalty
            )
            for (user_id, trust_score) in users["trust_score"].items()
            if user_id in user_models
        }

    ############################################
    ##  Methods to esimate the multiplicators ##
    ############################################

    def compute_model_norms(
        self,
        user_models: dict[int, ScoringModel],
        users: pd.DataFrame,
        entities: pd.DataFrame,
        privacy: PrivacySettings,
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
            user: _user_model_norms(
                user, 
                user_models[user], 
                entities, privacy, 
                self.p_norm_for_multiplicative_resilience, 
                self.privacy_penalty
            )
            for user in users.index
            if user in user_models
        }

    def compute_entity_ratios(
        self, 
        scalee_models: dict[int, ScoringModel],
        scaler_models: dict[int, ScoringModel],
        entities: pd.DataFrame,
        privacy: PrivacySettings
    ) -> dict[int, dict[int, tuple[list[float], list[float], list[float], list[float]]]]:
        """ Computes the ratios of score differences, with uncertainties,
        for comparable entities of any pair of scalers (s_{uvef} in paper),
        for u in scalees and v in scalers.
        Note that the output rations[u][v] is given as a 1-dimensional np.ndarray
        without any reference to e and f.
        
        Parameters
        ----------
        user_models: dict[int, ScoringModel]
            user_models[user] is a scoring model
        entities: DataFrame with columns
            * entity_id (int, index)
        scalees: DataFrame with columns
            * user_id (int, index)
        scalers: DataFrame with columns
            * user_id (int, index)
        privacy: PrivacySettings
        
        Returns
        -------
        out: dict[int, dict[int, tuple[list[float], list[float], list[float], list[float]]]]
            out[user][user_bis] is a tuple (ratios, voting_rights, lefts, rights),
            where ratios is a list of ratios of score differences,
            and left and right are the left and right ratio uncertainties.
        """
        user_entity_ratios = dict()
        entities_ids = set(entities.index)

        for u, u_model in scalee_models.items():
            user_entity_ratios[u] = dict()
            u_entities = entities_ids & u_model.scored_entities()
            if len(u_entities) == 0:
                continue

            for v, v_model in scaler_models.items():
                if u == v:
                    user_entity_ratios[u][v] = [1.], [1.], [0.], [0.]
                    continue

                uv_entities = list(u_entities & v_model.scored_entities())
                if len(entities) <= 1:
                    continue
                elif len(entities) <= 100:
                    ratios = self.load_all_ratios(u, v, uv_entities, entities, 
                        u_model, v_model, privacy)
                    if ratios is not None:
                        user_entity_ratios[u][v] = ratios
                else:
                    ratios = self.sample_ratios(u, v, uv_entities, entities, 
                        u_model, v_model, privacy)
                    if ratios is not None:
                        user_entity_ratios[u][v] = ratios

        return user_entity_ratios

    def load_all_ratios(
        self, 
        u: int, 
        v: int, 
        uv_entities: list[int], 
        entities: pd.DataFrame,
        u_model: ScoringModel, 
        v_model: ScoringModel, 
        privacy: Optional[PrivacySettings]
    ) -> Optional[tuple[
        list[float],
        list[float],
        list[float],
        list[float],
    ]]:
        ratios, voting_rights, lefts, rights = list(), list(), list(), list()
        for e, f in UnorderedPairs(uv_entities):
            output_u = _compute_abs_diff(u_model, e, f, entities)
            if output_u is None:
                continue
            output_v = _compute_abs_diff(v_model, e, f, entities)
            if output_v is None:
                continue

            voting_right = 1.0
            if privacy is not None:
                if privacy[u, f]:
                    voting_right *= self.privacy_penalty
                if privacy[v, f]:
                    voting_right *= self.privacy_penalty
            voting_rights.append(voting_right)

            diff_u, left_u, right_u = output_u
            diff_v, left_v, right_v = output_v
            ratio = np.abs(diff_v / diff_u)
            ratios.append(ratio)
            lefts.append(ratio - np.abs((diff_v - left_v) / (diff_u + right_u)))
            rights.append(np.abs((diff_v + right_v) / (diff_u - left_u)) - ratio)

        if len(voting_rights) == 0:
            return None

        return ratios, voting_rights, lefts, rights

    def sample_ratios(
        self, 
        u: int, 
        v: int, 
        uv_entities: list[int], 
        entities: pd.DataFrame,
        u_model: ScoringModel, 
        v_model: ScoringModel, 
        privacy: Optional[PrivacySettings]
    ) -> tuple[list[float], list[float], list[float], list[float]]:
        ratios, voting_rights, lefts, rights = list(), list(), list(), list()

        for e, f in UnorderedPairs(uv_entities).n_samples(self.n_diffs_sample_max):
            output_u = _compute_abs_diff(u_model, e, f, entities)
            if output_u is None:
                continue
            output_v = _compute_abs_diff(v_model, e, f, entities)
            if output_v is None:
                continue

            voting_right = 1.0
            if privacy is not None:
                if privacy[u, f]:
                    voting_right *= self.privacy_penalty
                if privacy[v, f]:
                    voting_right *= self.privacy_penalty
            voting_rights.append(voting_right)

            diff_u, left_u, right_u = output_u
            diff_v, left_v, right_v = output_v
            ratio = np.abs(diff_v / diff_u)
            ratios.append(ratio)
            lefts.append(ratio - np.abs((diff_v - left_v) / (diff_u + right_u)))
            rights.append(np.abs((diff_v + right_v) / (diff_u - left_u)) - ratio)
        return ratios, voting_rights, lefts, rights

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

def _computer_user_activities(
    user: int,
    user_model: ScoringModel, 
    entities: pd.DataFrame,
    trust_score: float,
    privacy: Optional[PrivacySettings],
    privacy_penalty: float
) -> float:
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
    if trust_score <= 0.0:
        return 0.0

    results = 0.0
    entity_ids = set(entities.index)
    for entity_id, (score, left, right) in user_model.iter_entities():
        if entity_id not in entity_ids:
            continue
        if score <= left and score >= -right:
            # Uncertainty interval contains 0
            # Sign of score is uncertain.
            continue
        added_quantity = 1.0
        if privacy is not None and privacy[user, entity_id]:
            added_quantity *= privacy_penalty
        results += added_quantity
    
    return results * trust_score

def _user_model_norms(
    user: int,
    user_model: ScoringModel,
    entities: pd.DataFrame,
    privacy: PrivacySettings,
    power: float,
    privacy_penalty: float
) -> float:
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
    weight_sum, weighted_sum = 0., 0.
    for (entity_id, (score, left_unc, right_unc)) in user_model.iter_entities(entities):
        weight = 1.0
        if privacy is not None and privacy[user, entity_id]:
            weight *= privacy_penalty
        
        weight_sum += weight
        weighted_sum += weight * (score**power)

    if weight_sum == 0:
        return 1.0

    return np.power(weighted_sum / weight_sum, 1 / power)

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
