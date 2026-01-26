from abc import abstractmethod

from copy import deepcopy
from typing import Any, Callable
from numpy.typing import NDArray
from numba import njit

import numpy as np
import logging
logger = logging.getLogger(__name__)

from solidago.poll import *
from solidago.functions.parallelized import ParallelizedPollFunction


class ParallelizedPreferenceLearning(ParallelizedPollFunction):
    def __init__(self, 
        max_workers: int = 1,
        direct: bool = True,
        categories: list[str] | None = None,
        n_parameters: int = 0,
        minimizer: tuple[str, dict] | None = None,
        uncertainty: tuple[str, dict] | None = None,
        keep_user_model_score_processing: bool = False,
    ):
        """ This class distributes preference learning per user and per criterion 
        Moreover, the learned values are derived from a minimizer,
        and the uncertainties are derived from an uncertainty evaluator.
        It is however agnostic to the scoring model used by the preference learning algorithm.
        """
        super().__init__(max_workers)
        self.direct, self.categories, self.n_parameters = direct, categories or list(), n_parameters
        self.keep_user_model_score_processing = keep_user_model_score_processing
        
        import solidago
        minimizer = ("SciPyMinimizer", dict()) if minimizer is None else minimizer
        self.minimizer = solidago.primitives.minimizer.Minimizer.load(minimizer)

        uncertainty = ("NLLIncrease", dict()) if uncertainty is None else uncertainty
        self.uncertainty = solidago.primitives.uncertainty.UncertaintyEvaluator.load(uncertainty)

    #############################################
    ##  Methods to be specified in subclasses  ##
    #############################################

    @abstractmethod
    def _rating_arg(self, ratings: Ratings, entities: Entities) -> tuple[NDArray, NDArray]:
        """ Returns entity_indices and normalized_ratings. May return more. """
    
    @abstractmethod
    def _comparison_arg(self, comparisons: Comparisons, entities: Entities) -> tuple[NDArray, NDArray, NDArray]: 
        """ Returns compared entity indices and normalized comparisons. May return more. """
        
    @abstractmethod    
    def prior_loss(self, values: NDArray, *args) -> float:
        """ The terminology is chosen to match considering the loss as a negative log-posterior.
        Some machine learning practitioners might be more used to name this as the "regularization term". """

    @abstractmethod
    def gradient(self, values: NDArray, *args) -> NDArray:
        """ Gradient function """
    
    @abstractmethod
    def nlls(self, values: NDArray, *args) -> NDArray:
        """ Negative log-likelihoods for the different observed data """

    @abstractmethod
    def translated_prior(self, value_index: int, values: NDArray, *args) -> Callable[[float], float]:
        """ Computes the coordinate-wise value of the prior. Used for uncertainty computation """

    @abstractmethod
    def hess_diagonal(self, values: NDArray, *args) -> NDArray:
        """ Computes the diagonal of the Hessian matrix. Can be used for uncertainty computation """

    #######################
    ##  Data management  ##
    #######################

    def _nonargs(self, 
        variable: tuple[User, str], 
        entities: Entities, 
        ratings: Ratings,
        comparisons: Comparisons,
    ) -> tuple[Entities, list[tuple[str, list[str]]], list[str]]:
        """ Helps determine the evaluated entities and the category groups """
        user, criterion = variable
        evaluated_entity_names = ratings[user, criterion].keys("entity_name")
        evaluated_entity_names |= comparisons[user, criterion].keys("entity_name")
        evaluated_entities = entities[evaluated_entity_names]
        category_groups = [(c, list({getattr(e, c) for e in evaluated_entities})) for c in self.categories]
        rating_contexts = list({a.context for _, a in ratings[user, criterion]})
        return evaluated_entities, category_groups, rating_contexts

    def _variables(self, users: Users, ratings: Ratings, comparisons: Comparisons) -> list[tuple[User, str]]:
        return [
            (user, criterion)
            for user in users
            for criterion in ratings[user].keys("criterion") | comparisons[user].keys("criterion")
        ]

    def _args(self, 
        variable: tuple[User, str], 
        nonargs: tuple[Entities, list[tuple[str, list[str]]], list[str]], 
        ratings: Ratings,
        comparisons: Comparisons,
        user_models: UserModels,
    ) -> list[NDArray, tuple[NDArray, NDArray], tuple[NDArray, NDArray, NDArray], NDArray, NDArray, bool, int, NDArray, int]:
        """ 
        Returns
        ------ 
        init_value,
        ratings, comparisons, embedding_matrix, category_indices, 
        direct, n_entities, n_thresholds, category_group_lengths, n_parameters """
        user, criterion = variable
        entities, category_groups, rating_contexts = nonargs 
        n_entities, n_thresholds = len(entities), len(rating_contexts)
        category_indices = self._category_indices(entities, category_groups, len(entities), n_thresholds)
        return (
            self._init_model_arg(user_models[user], criterion, entities, user, rating_contexts, category_groups),
            self._rating_arg(ratings[user, criterion], entities, rating_contexts),
            self._comparison_arg(comparisons[user, criterion], entities),
            entities.vectors[:, :self.n_parameters],
            category_indices,
            self.direct,
            n_entities,
            n_thresholds,
            np.array([len(groups) for _, groups in category_groups]), 
            self.n_parameters
        )

    def _init_model_arg(self, 
        model: ScoringModel, 
        criterion: str, 
        entities: Entities, 
        user: User,
        rating_contexts: list[str],
        category_groups: list[tuple[str, list[str]]],
    ) -> NDArray:
        """ Assumes that each rating context requires an additional variable, called `threshold`.
        This is the case for FlexibleGeneralizedBradleyTerry, but could require modifications for other
        preference learning algorithms """
        directs = [model.directs[entity, criterion].value for entity in entities]
        thresholds = [user[context] if context in user else 0.0 for context in rating_contexts]
        categories = [
            model.categories[category, group, criterion].value
            for category, groups in category_groups
            for group in groups
        ]
        model_parameters = model.parameters.values(criterion)[:self.n_parameters]
        n_missing_parameter_values = self.n_parameters - len(model_parameters)
        parameters = np.concatenate([model_parameters, np.zeros(n_missing_parameter_values)])
        nonparameteric_variables = np.nan_to_num(np.array(directs + thresholds + categories))
        return np.concatenate([nonparameteric_variables, parameters])
    
    def _category_indices(self, entities: Entities, category_groups: list[tuple[str, list[str]]], n_entities: int, n_thresholds: int) -> NDArray:
        """ Returns indices such that indices[entity_index, category_index] is the index 
        of the group of entity within category. 
        Thus indices is of shape (len(entities), len(category_list)), with dtype np.int64 """
        offset = n_thresholds + (n_entities if self.direct else 0)
        offsets = list()
        for _, groups in category_groups:
            offsets.append(offset)
            offset += len(groups)
        return np.array([
            [o + g.index(getattr(e, c)) for o, (c, g) in zip(offsets, category_groups)] 
            for e in entities
        ])

    def _process_results(self, 
        variables: list[tuple[User, str]], 
        nonargs_list: list[tuple[Entities, list[tuple[str, list[str]]], list[str]]], 
        results: list[tuple[NDArray, NDArray, NDArray]], 
        args_lists: list[NDArray, tuple[NDArray, NDArray], tuple[NDArray, NDArray, NDArray], NDArray, NDArray], 
        users: Users,
        entities: Entities,
        ratings: Ratings,
        comparisons: Comparisons,
        user_models: UserModels,
    ) -> tuple[Users, Entities, UserModels]:
        """ Assumes that each rating context requires an additional variable, called `threshold`.
        This is the case for FlexibleGeneralizedBradleyTerry, but could require modifications for other
        preference learning algorithms """
        composition, user_compositions = self._returned_model_composition(), dict()
        default_composition = [composition]

        if self.keep_user_model_score_processing:
            default_composition = deepcopy(user_models.default_composition)
            default_composition[0] = composition
            user_compositions = deepcopy(user_models.user_compositions)
            for username in user_compositions:
                user_compositions[username][0] = composition

        from solidago.poll.scoring.user_models import UserDirectScores, UserCategoryScores, UserParameters
        user_directs, user_categories = UserDirectScores(), UserCategoryScores()
        user_parameters = UserParameters()

        for (user, criterion), nonargs, (values, lefts, rights) in zip(variables, nonargs_list, results):
            entities, category_groups, rating_contexts = nonargs
            i = 0
            for entity in entities:
                user_directs[user, entity, criterion] = Score(values[i], lefts[i], rights[i])
                i += 1
            for context in rating_contexts:
                user[f"rating_threshold_{context}_value"] = values[i]
                user[f"rating_threshold_{context}_left_uncertainty"] = lefts[i]
                user[f"rating_threshold_{context}_right_uncertainty"] = rights[i]
                i += 1
            for category, groups in category_groups:
                for group in groups:
                    user_categories[user, category, group, criterion] = Score(values[i], lefts[i], rights[i])
                    i += 1
            for j in range(i, len(entities)):
                user_parameters[user, criterion, str(j)] = Score(values[i+j], lefts[i+j], rights[i+j])
        
        users = self.add_user_stats(users, ratings, comparisons)
        entities = self.add_entity_stats(entities, ratings, comparisons)

        args = () if not self.keep_user_model_score_processing else (
            user_models.user_multipliers, user_models.user_translations,
            user_models.common_multipliers, user_models.common_translations,
        )

        user_models = UserModels(
            default_composition, user_compositions,
            user_directs, user_categories, user_parameters, *args
        )
        
        return users, entities, user_models

    def add_user_stats(self, users: Users, ratings: Ratings, comparisons: Comparisons) -> Users:
        evaluated_entities = lambda u: ratings[u].keys("entity_name") | comparisons[u].keys("entity_name")
        return users.assign(
            n_ratings=[len(ratings[u]) for u in users], 
            n_comparisons=[len(comparisons[u]) for u in users], 
            n_evaluated_entities=[len(evaluated_entities(u)) for u in users]
        )
    
    def add_entity_stats(self, entities: Entities, ratings: Ratings, comparisons: Comparisons) -> Entities:
        ratings = ratings.reorder("entity_name", "username", "criterion")
        comparisons = comparisons.reorder("entity_name", "username", "criterion")
        evaluators = lambda e: ratings[e].keys("username") | comparisons[e].keys("username")
        return entities.assign(
            n_ratings=[len(ratings[e]) for e in entities], 
            n_comparisons=[len(comparisons[e]) for e in entities], 
            n_raters=[len(ratings[e].keys("username")) for e in entities], 
            n_comparers=[len(comparisons[e].keys("username")) for e in entities], 
            n_evaluators=[len(evaluators(e)) for e in entities]
        )

    def save_result(self, poll: Poll, directory: str | None = None) -> tuple[str, dict]:
        if directory is not None:
            logger.info("Saving user base model")
            poll.user_models.save_table(directory, "user_directs")
            poll.user_models.save_table(directory, "user_categories")
            poll.user_models.save_table(directory, "user_parameters")
        logger.info("Saving poll.yaml")
        return poll.save_instructions(directory)
 
    def _returned_model_composition(self) -> tuple[str, dict]:
        """ This assumes model linearity. It should be modified for non-linear models """
        base_scoring = "Linear"
        if self.n_parameters == 0:
            base_scoring = "MetaAndData" if self.categories else "Direct"
        return base_scoring, dict(note=type(self).__name__)
       
    ########################################
    ##  Core preference learning methods  ##
    ########################################

    def thread_function(self, init: NDArray, *args) -> tuple[NDArray, NDArray, NDArray]:
        """ Must return parameters and left/right uncertainties """
        values = self.compute_values(init, *args)
        left_uncertainties, right_uncertainties = self.compute_uncertainties(values, *args)
        return values, left_uncertainties, right_uncertainties
    
    def compute_values(self, init: NDArray, *args) -> NDArray:
        """ Computes the values given comparisons by minimizing a loss function, using gradients and/or partial derivatives """
        return self.minimizer(init, args, self.loss, self.gradient, self.partial_derivatives)

    def compute_uncertainties(self, values: NDArray, *args) -> tuple[NDArray, NDArray]:
        """ Given learned maximum-a-posteriori values, determines uncertainties """
        return self.uncertainty(values, args, self.translated_nll, self.translated_prior, self.hess_diagonal)
    
    #################################################################
    ## Derived methods. They could be optimized in derived classes ##
    #################################################################

    def partial_derivatives(self, value_index: int, values: NDArray, *args) -> Callable[[float], float]:
        def g(value: float) -> float:
            old_value = values[value_index]
            values[value_index] = value
            gradient = self.gradient(values, *args)[value_index]
            values[value_index] = old_value
            return gradient
        return g

    def loss(self, values: NDArray, *args) -> float:
        return self.prior_loss(values, *args) + self.nll(values, *args)

    def nll(self, values: NDArray, *args) -> float:
        return self.nlls(values, *args).sum()
    
    def translated_nll(self, value_index: int, values: NDArray, *args) -> Callable[[float], float]:
        """ Computes the negative log-likelihood (up to a constant) restricted to an entity,
        and to the comparisons that involve this entity. The function depends on given fixed values,
        and aims to estimate the variations in likelihood for a coordinate-wise variation. 
        This is used for uncertainty computation """
        assert value_index < len(values), (value_index, values)
        assert isinstance(value_index, int), value_index
        assert value_index >= 0, value_index
        assert isinstance(values, np.ndarray), values
        base_vector = np.zeros(len(values))
        base_vector[value_index] = 1
        def f(delta: float) -> float:
            return self.nll(values + delta * base_vector, *args)
        return f