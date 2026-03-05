import itertools
from typing import Callable, Hashable
from numpy.typing import NDArray

import numpy as np
import logging

logger = logging.getLogger(__name__)

from solidago.poll.scoring.user_models import UserMultipliers, UserTranslations
from solidago.primitives.lipschitz import qr_median, qr_uncertainty
from solidago.primitives.pairs import UnorderedPairs
from solidago.poll import *
from solidago.poll_functions.poll_function import PollFunction


class Mehestan(PollFunction):
    def __init__(self, 
        lipschitz: float=0.1, 
        min_scaler_activity: float=10.0,
        n_scalers_max: int=100, 
        privacy_penalty: float=0.5,
        user_comparison_lipschitz: float=10.0,
        p_norm_for_multiplicative_resilience: float=4.0,
        n_entity_to_fully_compare_max: float=100,
        n_diffs_sample_max: int=1000,
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

    """ A simple way to distribute computations is to parallelize the loop of fn """
    def fn(self, 
        users: Users,
        entities: Entities,
        public_settings: PublicSettings,
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
        scores = user_models(entities)
        criteria = list(user_models.criteria())
        results = [self.scale_criterion(users, entities, public_settings, scores.filters(criterion=c)) for c in criteria]
        keynames = ["username", "criterion"]
        multipliers, translations, kwargs = UserMultipliers(keynames=keynames), UserTranslations(keynames=keynames), dict()
        for criterion, (submultipliers, subtranslations, activities, is_scaler) in zip(criteria, results):
            multipliers = multipliers | submultipliers.add_keys(criterion=criterion)
            translations = translations | subtranslations.add_keys(criterion=criterion)
            kwargs[f"activities_{criterion}"] = activities
            kwargs[f"is_scaler_{criterion}"] = is_scaler
        return users.assign(**kwargs), user_models.user_scale(multipliers, translations, note="mehestan")

    def save_result(self, poll: Poll, directory: str | None = None) -> tuple[str, dict]:
        if directory is not None:
            poll.users.save(directory)
            poll.user_models.save_table(directory, "user_multipliers")
            poll.user_models.save_table(directory, "user_translations")
        return poll.save_instructions(directory)
    
    def scale_criterion(self, 
        users: Users,
        entities: Entities,
        public_settings: PublicSettings, # keynames == ["username", "entity_name"]
        scores: Scores,
    ) -> tuple[UserMultipliers, UserTranslations, NDArray, NDArray]: # scales, activies, is_scaler
        activities, is_scaler = self.compute_activities_and_scalers(users, public_settings, scores)
        if not any(is_scaler):
            logger.warning("  No user qualifies as a scaler. No scaling performed.")
            return UserMultipliers(keynames=["username"]), UserTranslations(keynames=["username"]), activities, is_scaler
        scalers, nonscalers = set(), set()
        for index, user in enumerate(users):
            (scalers if is_scaler[index] else nonscalers).add(user.name)
        
        scaler_scores, nonscaler_scores = scores.filters(username=list(scalers)), scores.filters(username=list(nonscalers))
        scale_scalers_to_scalers_args = (users, public_settings, scaler_scores, scaler_scores, True)
        scaler_multipliers, scaler_translations, scaler_scores = self.scale_to_scalers(*scale_scalers_to_scalers_args)

        scale_nonscalers_to_scalers_args = (users, public_settings, scaler_scores, nonscaler_scores)
        nonscaler_multipliers, nonscaler_translations, _ = self.scale_to_scalers(*scale_nonscalers_to_scalers_args)
        
        multipliers = scaler_multipliers | nonscaler_multipliers
        translations = scaler_translations | nonscaler_translations

        return multipliers, translations, activities, is_scaler

    ############################################
    ##  The three main steps are              ##
    ##  1. Select the subset of scalers       ##
    ##  2. Scale the scalers                  ##
    ##  3. Fit the nonscalers to the scalers  ##
    ############################################

    def compute_activities_and_scalers(self,
        users: Users,
        public_settings: PublicSettings, # keynames == ["username", "entity_name"]
        scores: Scores, # keynames == ["username", "entity_name"]
    ) -> tuple[NDArray, NDArray]:
        """ Determines which users will be scalers.
        The set of scalers is restricted for two reasons.
        First, too inactive users are removed, because their lack of comparability
        with other users makes the scaling process ineffective.
        Second, scaling scalers is the most computationally demanding step of Mehestan.
        Reducing the number of scalers accelerates the computation (often a bottleneck).
            
        Returns
        -------
        is_scaler: NDArray
            is_scaler[i] says whether username at iloc i in users is a scaler
        """
        activities = self.compute_activities(users, public_settings, scores) # NDArray
        argsort = np.argsort(activities)
        is_scaler = np.array([False] * len(activities))
        for user_index in range(min(self.n_scalers_max, len(activities))):
            if activities[argsort[-user_index-1]] < self.min_scaler_activity:
                break
            is_scaler[argsort[-user_index-1]] = True
        return activities, is_scaler

    def scale_to_scalers(self, 
        users: Users,
        public_settings: PublicSettings, # keynames == ["username", "entity_name"]
        scaler_scores: Scores, # keynames == ["username", "entity_name"]
        scalee_scores: Scores, # keynames == ["username", "entity_name"]
        scalees_are_scalers: bool=False
    ) -> tuple[UserMultipliers, UserTranslations, Scores]: # scalee_scales, scalee_scores
        scalee_model_norms = self.compute_model_norms(public_settings, scalee_scores)
    
        ratio_weight_lists, ratio_lists = self.ratios(public_settings, scaler_scores, scalee_scores)
        ratio_args = users, ratio_weight_lists, ratio_lists, self.default_multiplier_dev
        voting_rights, ratios = self.aggregate_scaler_scores(*ratio_args)
        multipliers = self.compute_multipliers(voting_rights, ratios, scalee_model_norms)
        for score in scalee_scores:
            multiplied_score = score * multipliers.get(username=score["username"])
            assert isinstance(multiplied_score, Score)
            scalee_scores.set(multiplied_score)
        if scalees_are_scalers:
            scaler_scores = scalee_scores
    
        diff_weight_lists, diff_lists = self.diffs(public_settings, scaler_scores, scalee_scores)
        diff_args = users, diff_weight_lists, diff_lists, self.default_translation_dev
        voting_rights, diffs = self.aggregate_scaler_scores(*diff_args)
        translations = self.compute_translations(voting_rights, diffs)
        for score in scalee_scores:
            translated_score = score + translations.get(username=score["username"])
            assert isinstance(translated_score, Score)
            scalee_scores.set(translated_score)
    
        return multipliers, translations, scalee_scores

    ############################################
    ##    Methods to estimate the scalers     ##
    ############################################

    def compute_activities(self,
        users: Users, 
        public_settings: PublicSettings, # keynames == ["username", "entity_name"]
        scores: Scores, # keynames == ["username", "entity_name"]
    ) -> NDArray:
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
        activities: NDArray
            activities[i] is a measure of user i's trustworthy activeness,
            where i is the iloc of the user in users
        """
        return np.array([
            self.compute_user_activities(
                user["trust"], 
                public_settings.filters(username=user.name), 
                scores.filters(username=user.name)
            ) for user in users
        ])
    
    def compute_user_activities(self,
        trust: float,
        public_settings: PublicSettings, # keynames = ["entity_name"]
        scores: Scores, # keynames = ["entity_name"]
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
            public_settings.penalty(self.privacy_penalty, score["entity_name"])
            for score in scores if not score.contains(0)
        ])
        
        return trust * sum_of_activities

    #############################################################
    ##  Methods used for both multipliers and translations  ##
    #############################################################

    def scaler_scalee_comparison_lists(self, 
        public_settings: PublicSettings, # keynames == ["username", "entity_name"]
        scalers_scores: Scores, # keynames == ["username", "entity_name"]
        scalees_scores: Scores, # keynames == ["username", "entity_name"]
        compute_scaler_scalee_comparisons: Callable[["Mehestan", Scores, Scores, PublicSettings, set[Hashable]], tuple[VotingRights, Scores]],
        default_value: Score,
    ) -> tuple[VotingRights, Scores]: # keynames == ["scalee_name", "scaler_name"]
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
        weights = VotingRights(keynames=["scalee_name", "scaler_name"])
        comparisons = Scores(keynames=["scalee_name", "scaler_name"])
        
        for scalee_name in scalees_scores.keys("username"):
            scalee_scores = scalees_scores.filters(username=scalee_name) # keynames == ["entity_name"]
            entity_names = scalee_scores.keys("entity_name")
            scaler_names = set.union(*[scalers_scores.filters(entity_name=e).keys("username") for e in entity_names])
            
            for scaler_name in scaler_names:
                
                if scalee_name == scaler_name:
                    weights.set(scalee_name=scalee_name, scaler_name=scaler_name, voting_right=1.)
                    comparisons.set(Score(default_value), scalee_name=scalee_name, scaler_name=scaler_name)
                    continue
                
                scaler_scores = scalers_scores.filters(username=scaler_name) # keynames == ["entity_name"]
                common_entity_names = entity_names & scaler_scores.keys("entity_name")
                args = (scalee_scores, scaler_scores, public_settings.filters(username=scaler_name), common_entity_names)
                sub_weights, sub_comparisons = compute_scaler_scalee_comparisons(self, *args)
                weights = weights | sub_weights.add_keys(scaler_name=scaler_name, scalee_name=scalee_name)
                comparisons = comparisons | sub_comparisons.add_keys(scaler_name=scaler_name, scalee_name=scalee_name)

        return weights, comparisons
    
    def aggregate_scaler_scores(self,
        users: Users,
        full_weights: VotingRights, # keynames == ["scalee_name", "scaler_name"], value_cls == list
        full_scores: Scores, # keynames == ["scalee_name", "scaler_name"], value_cls == list
        default_dev: float,
    ) -> tuple[VotingRights, Scores]: # keynames == ["scalee_name", "scaler_name"]
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
        multiscores: Scores
            With keynames == ["scalee_name", "scaler_name"]
        """
        voting_rights = VotingRights(keynames=["scalee_name", "scaler_name"])
        scores = Scores(keynames=["scalee_name", "scaler_name"])
        
        common_kwargs = dict(lipschitz=self.user_comparison_lipschitz, error=self.error)
        for scalee_name, scaler_name in itertools.product(scores.keys("scaler_name"), scores.keys("scalee_name")):
            filtered_weights = full_weights.filters(scalee_name=scalee_name, scaler_name=scaler_name)
            filtered_scores = full_scores.filters(scalee_name=scalee_name, scaler_name=scaler_name)
            kwargs = common_kwargs | dict(
                values=filtered_scores.value,
                voting_rights=filtered_weights.get_column("voting_right").to_numpy(np.float64),
                left_unc=filtered_scores.left_unc,
                right_unc=filtered_scores.right_unc,
            )
            value = qr_median(**kwargs) # type: ignore
            uncertainty = qr_uncertainty(median=value, default_dev=default_dev, **kwargs) # type: ignore
            scores.set(Score((value, uncertainty, uncertainty)), scalee_name=scalee_name, scaler_name=scaler_name)
            voting_rights.set(scalee_name=scalee_name, scaler_name=scaler_name, voting_right=users[scaler_name]["trust"])
                
        return voting_rights, scores

    def aggregate_scalers(self,
        voting_rights: VotingRights, # keynames = ["scaler_name"]
        scores: Scores, # keynames = ["scaler_name"]
        lipschitz: float,
        default_value: float, 
        default_dev: float, 
        aggregator: Callable[
            [float, NDArray[np.float64], NDArray[np.float64], NDArray[np.float64], NDArray[np.float64], float, float], 
            float
        ] = qr_median,
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
            voting_rights=voting_rights.get_column("voting_right").to_numpy(np.float64),
            values=scores.value,
            left_unc=scores.left_unc,
            right_unc=scores.right_unc,
            error=self.error
        )
        value = aggregator(default_value=default_value, **kwargs) # type: ignore
        uncertainty = qr_uncertainty(median=value if aggregator is qr_median else None, **kwargs) # type: ignore
        return Score((value, uncertainty, uncertainty))


    ############################################
    ##  Methods to esimate the multipliers ##
    ############################################

    def compute_model_norms(self,
        public_settings: PublicSettings, # keynames == ["username", "entity_name"]
        scores: Scores, # keynames == ["username", "entity_name"]
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
            str(username): self.compute_model_norm(
                public_settings.filters(username=username), 
                scores.filters(username=username)
            ) for username in scores.keys("username")
        }

    def compute_model_norm(self, public_settings: PublicSettings, scores: Scores) -> float:
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
        for score in scores:
            weight = public_settings.penalty(self.privacy_penalty, score["entity_name"])
            weight_sum += weight
            weighted_sum += weight * (score.value**self.p_norm_for_multiplicative_resilience)
    
        if weight_sum == 0:
            return 1.0
    
        return np.power(weighted_sum / weight_sum, 1 / self.p_norm_for_multiplicative_resilience)

    def ratios(self, 
        public_settings: PublicSettings, # keynames == ["username", "entity_name"]
        scaler_scores: Scores, # keynames == ["username", "entity_name"]
        scalee_scores: Scores, # keynames == ["username", "entity_name"]
    ) -> tuple[VotingRights, Scores]: # keynames == ["scalee_name", "scaler_name"]
        """ Computes the ratios of score differences, with uncertainties,
        for comparable entities of any pair of scalers (s_{uvef} in paper),
        for u in scalees and v in scalers.
        
        Parameters
        ----------
        made_public: MadePublic
            Must have keynames == ["username", "entity_name"]
        scalee_scores: Scores
            Must have keynames == ["username", "entity_name"]
        scaler_scores: Scores
            Must have keynames == ["username", "entity_name"]
        
        Returns
        -------
        weight_lists: VotingRights
            With keynames == ["scalee_name", "scaler_name"] and last_only == False
            weight_lists.get(scalee_name, scaler_name) is a list of weights, for pairs
            of entities.
        ratio_lists: Scores
            With keynames == ["scalee_name", "scaler_name"] and last_only == False
            multiscore.get(scalee_name, scaler_name) is a list of ratios of score differences,
            each of which is of type Score.
        """
        args = (public_settings, scaler_scores, scalee_scores, Mehestan.compute_ratios, Score(1))
        return self.scaler_scalee_comparison_lists(*args)

    def compute_ratios(self,
        scalee_scores: Scores, # key_name == ["entity_name"]
        scaler_scores: Scores, # key_name == ["entity_name"]
        scaler_public: PublicSettings, # key_name == ["entity_name"]
        common_entity_names: set[Hashable],
    ) -> tuple[VotingRights, Scores]: # keynames == ["scalee_name", "scaler_name"]
        """ Returns the scaler's voting right and ratios to multiplicatively scale scalee's model """
        if len(common_entity_names) <= 1:
            return VotingRights(keynames=["scalee_name", "scaler_name"]), Scores(keynames=["scalee_name", "scaler_name"])
        pairs = UnorderedPairs(common_entity_names)
        if len(common_entity_names) > self.n_entity_to_fully_compare_max:
            pairs = pairs.n_samples(self.n_diffs_sample_max)
        weight_list, ratio_list = VotingRights(keynames=[]), Scores(keynames=[])
        penalty = lambda entity_name: scaler_public.penalty(self.privacy_penalty, entity_name)
        for e, f in pairs:
            scalee_diff = scalee_scores.get(entity_name=e) - scalee_scores.get(entity_name=f)
            assert isinstance(scalee_diff, Score)
            if scalee_diff.contains(0): 
                continue
            scaler_diff = scaler_scores.get(entity_name=e) - scaler_scores.get(entity_name=f)
            ratio = scaler_diff / scalee_diff
            assert isinstance(ratio, Score)
            ratio_list.append(ratio.abs())
            weight = penalty(e) * penalty(f)
            weight_list.append(voting_right=weight)
        return weight_list, ratio_list

    def compute_multipliers(self, 
        voting_rights: VotingRights, # keynames == ["scalee_name", "scaler_name"]
        ratios: Scores, # keynames == ["scalee_name", "scaler_name"]
        model_norms: dict[str, float]
    ) -> UserMultipliers: # keynames = ["username"]
        """ Computes the multipliers of users with given user_ratios """
        kwargs = dict(default_value=1.0, default_dev=self.default_multiplier_dev)
        multipliers = UserMultipliers(keynames=["username"])
        for (scalee_name,), weights in voting_rights.iter("scalee_name"):
            assert isinstance(weights, VotingRights)
            subratios = ratios.filters(scalee_name=scalee_name)
            lipschitz = self.lipschitz / (8 * (1e-9 + model_norms[str(scalee_name)]))
            multipliers.append(self.aggregate_scalers(weights, subratios, lipschitz, **kwargs)) # type: ignore
        return multipliers

    ############################################
    ##   Methods to esimate the translations  ##
    ############################################
    
    def diffs(self, 
        public_settings: PublicSettings, # keynames == ["username", "entity_name"]
        scaler_scores: Scores, # keynames == ["username", "entity_name"]
        scalee_scores: Scores, # keynames == ["username", "entity_name"]
    ) -> tuple[VotingRights, Scores]: # keynames == ["scalee_name", "scaler_name"]
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
        args = (public_settings, scaler_scores, scalee_scores, Mehestan.compute_diffs, Score(0.))
        return self.scaler_scalee_comparison_lists(*args)

    def compute_diffs(self,
        scalee_scores: Scores, # key_name == ["entity_name"]
        scaler_scores: Scores, # key_name == ["entity_name"]
        scaler_public: PublicSettings, # key_name == ["entity_name"]
        common_entity_names: set[Hashable],
    ) -> tuple[VotingRights, Scores]:
        """ Returns the scaler's voting right and ratios to multiplicatively scale scalee's model """
        weight_list, diff_list = VotingRights(keynames=[]), Scores(keynames=[])
        penalty = lambda entity_name: scaler_public.penalty(self.privacy_penalty, entity_name)
        for entity_name in common_entity_names:
            weight_list.append(value=scaler_public.penalty(self.privacy_penalty, entity_name))
            diff = scaler_scores.get(entity_name=entity_name) - scalee_scores.get(entity_name=entity_name)
            assert isinstance(diff, Score)
            diff_list.append(diff)
        return weight_list, diff_list

    def compute_translations(self, 
        voting_rights: VotingRights, # keynames == ["scalee_name", "scaler_name"]
        diffs: Scores, # keynames == ["scalee_name", "scaler_name"]
    ) -> UserTranslations: # keynames = ["scalee_name"]
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
        translations = UserTranslations(keynames=["username"])
        for (scalee_name,), weights in voting_rights.iter("scalee_name"):
            assert isinstance(weights, VotingRights)
            subdiffs = diffs.filters(scalee_name=scalee_name)
            translations.append(self.aggregate_scalers(weights, subdiffs, **kwargs)) # type: ignore
        return translations

