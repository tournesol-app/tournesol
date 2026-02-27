from abc import abstractmethod

from copy import deepcopy
from typing import Any, Callable
from numpy.typing import NDArray

import numpy as np
import logging

from solidago.primitives.minimizer.minimizer import Minimizer
from solidago.primitives.timer import time
from solidago.primitives.uncertainty.uncertainty_evaluator import UncertaintyEvaluator
logger = logging.getLogger(__name__)

from solidago.poll import *
from solidago.poll_functions.parallelized import ParallelizedPollFunction


class ParallelizedPreferenceLearning(ParallelizedPollFunction):
    def __init__(self, 
        max_workers: int = 1,
        direct: bool = True,
        categories: list[str] | None = None,
        n_parameters: int = 0,
        minimizer: Minimizer | tuple[str, dict] | None = None,
        uncertainty: UncertaintyEvaluator | tuple[str, dict] | None = None,
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
        if not isinstance(minimizer, Minimizer):
            minimizer_cls, minimizer_kwargs = ("SciPyMinimizer", dict()) if minimizer is None else minimizer
            _minimizer = solidago.load(minimizer_cls, solidago.primitives.minimizer, **minimizer_kwargs)
            assert isinstance(_minimizer, Minimizer)
            minimizer = _minimizer
        self.minimizer = minimizer

        if not isinstance(uncertainty, UncertaintyEvaluator):
            uncertainty_cls, uncertainty_kwargs = ("NLLIncrease", dict()) if uncertainty is None else uncertainty
            _uncertainty = solidago.load(uncertainty_cls, solidago.primitives.uncertainty, **uncertainty_kwargs)
            assert isinstance(_uncertainty, UncertaintyEvaluator)
            uncertainty = _uncertainty
        self.uncertainty = uncertainty

    #############################################
    ##  Methods to be specified in subclasses  ##
    #############################################

    @abstractmethod
    def _rating_arg(self, 
        ratings: Ratings, 
        entities: Entities,
        rating_contexts: list[str],
    ) -> tuple[NDArray[np.int64], NDArray[np.float64]]:
        """ Returns entity_indices and normalized_ratings. May return more. """
    
    @abstractmethod
    def _comparison_arg(self, 
        comparisons: Comparisons, 
        entities: Entities
    ) -> tuple[NDArray[np.int64], NDArray[np.int64], NDArray[np.float64]]: 
        """ Returns compared entity indices and normalized comparisons. May return more. """
        
    @abstractmethod    
    def prior_loss(self, values: NDArray[np.float64], *args) -> float:
        """ The terminology is chosen to match considering the loss as a negative log-posterior.
        Some machine learning practitioners might be more used to name this as the "regularization term". """

    @abstractmethod
    def gradient(self, values: NDArray[np.float64], *args) -> NDArray[np.float64]:
        """ Gradient function """
    
    @abstractmethod
    def nlls(self, values: NDArray[np.float64], *args) -> NDArray[np.float64]:
        """ Negative log-likelihoods for the different observed data """

    @abstractmethod
    def hess_diagonal(self, values: NDArray[np.float64], *args) -> NDArray[np.float64]:
        """ Computes the diagonal of the Hessian matrix. Can be used for uncertainty computation """

    #######################
    ##  Data management  ##
    #######################

    def _nonargs(self,  # type: ignore
        variable: tuple[User, str], 
        entities: Entities, 
        ratings: Ratings,
        comparisons: Comparisons,
    ) -> tuple[Entities, list[tuple[str, list[str]]], list[str]]:
        """ Helps determine the evaluated entities and the category groups """
        user, criterion = variable
        filtered_ratings = ratings.filters(username=user.name, criterion=criterion)
        filtered_comparisons = comparisons.filters(username=user.name, criterion=criterion)
        evaluated_entity_names = ratings.filters(username=user.name, criterion=criterion).keys("entity_name")
        evaluated_entity_names |= filtered_comparisons.keys("left_name")
        evaluated_entity_names |= filtered_comparisons.keys("right_name")
        evaluated_entities = entities[list(evaluated_entity_names)]
        assert isinstance(evaluated_entities, Entities)
        rating_contexts = list({r["context"] for r in filtered_ratings})
        category_groups = [(c, list(evaluated_entities.get_column(str(c)))) for c in self.categories]
        return evaluated_entities, category_groups, rating_contexts

    def _variables(self, users: Users, ratings: Ratings, comparisons: Comparisons) -> list[tuple[User, str]]: # type: ignore
        return [
            (user, str(criterion))
            for user in users
            for criterion in ratings.filters(username=user.name).keys("criterion") \
                | comparisons.filters(username=user.name).keys("criterion")
        ]

    def _args(self,  # type: ignore
        variable: tuple[User, str], 
        nonargs: tuple[Entities, list[tuple[str, list[str]]], list[str]], 
        ratings: Ratings,
        comparisons: Comparisons,
        user_models: UserModels,
    ) -> tuple[
        NDArray[np.float64], # values
        tuple[NDArray[np.int64], NDArray[np.float64]], # entity_indices, ratings
        tuple[NDArray[np.int64], NDArray[np.int64], NDArray[np.float64]], # left_indices, right_indices, comparisons
        NDArray[np.float64], # embedding_matrix
        NDArray[np.int64], # category_indices
        bool, # direct
        np.int64, # n_entities
        np.int64, # n_thresholds
        NDArray[np.int64], # category_group_lengths
        np.int64, # n_parameters
    ]:
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
            self._rating_arg(ratings.filters(username=user.name, criterion=criterion), entities, rating_contexts),
            self._comparison_arg(comparisons.filters(username=user.name, criterion=criterion), entities),
            entities.vectors[:, :self.n_parameters].astype(np.float64),
            category_indices,
            self.direct,
            np.int64(n_entities),
            np.int64(n_thresholds),
            np.array([len(groups) for _, groups in category_groups], dtype=np.int64), 
            np.int64(self.n_parameters),
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
        directs = np.zeros(len(entities))
        for entity_index, entity in enumerate(entities):
            directs[entity_index] = model.directs.get(criterion=criterion, entity_name=entity.name).value
        thresholds = [
            user[f"rating_threshold_{context}_value"] if f"rating_threshold_{context}_value" in user else 0.0 
            for context in rating_contexts
        ]
        categories = [
            model.categories.get(category=category, group=group, criterion=criterion).value
            for category, groups in category_groups
            for group in groups
        ]
        model_parameters = model.parameters.values(criterion=criterion)[:self.n_parameters]
        n_missing_parameter_values = self.n_parameters - len(model_parameters)
        parameters = np.concatenate([model_parameters, np.zeros(n_missing_parameter_values)])
        nonparameteric_variables = np.nan_to_num(np.array(list(directs) + thresholds + categories))
        return np.concatenate([nonparameteric_variables, parameters], dtype=np.float64)
    
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
            [o + g.index(e[c]) for o, (c, g) in zip(offsets, category_groups)] 
            for e in entities
        ], dtype=np.int64)

    def _process_results(self,  # type: ignore
        variables: list[tuple[User, str]], 
        nonargs_list: list[tuple[Entities, list[tuple[str, list[str]]], list[str]]], 
        results: list[tuple[NDArray, NDArray, NDArray]], 
        args_lists: list[tuple], # not used
        users: Users,
        entities: Entities,
        ratings: Ratings,
        comparisons: Comparisons,
        user_models: UserModels,
    ) -> UserModels:
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
            user_criterion_kwargs = dict(username=user.name, criterion=criterion)
            for entity in entities:
                score = Score((values[i], lefts[i], rights[i]))
                user_directs.set(score, entity_name=entity.name, **user_criterion_kwargs)
                i += 1
            for context in rating_contexts:
                user[f"rating_threshold_{context}_value"] = values[i]
                user[f"rating_threshold_{context}_left_unc"] = lefts[i]
                user[f"rating_threshold_{context}_right_unc"] = rights[i]
                i += 1
            for category, groups in category_groups:
                for group in groups:
                    score = Score((values[i], lefts[i], rights[i]))
                    user_categories.set(score, category=category, group=group, **user_criterion_kwargs)
                    i += 1
            for j in range(i, len(entities)):
                score = Score((values[i+j], lefts[i+j], rights[i+j]))
                user_parameters.set(score, coordinate=j, **user_criterion_kwargs)
        
        args = () if not self.keep_user_model_score_processing else (
            user_models.user_multipliers, user_models.user_translations,
            user_models.common_multipliers, user_models.common_translations,
        )

        return UserModels(
            default_composition, user_compositions,
            user_directs, user_categories, user_parameters, 
            *args # type: ignore
        )

    def save_result(self, poll: Poll, directory: str | None = None) -> tuple[str, dict]:
        if directory is not None:
            poll.user_models.save_table(directory, "user_directs")
            poll.user_models.save_table(directory, "user_categories")
            poll.user_models.save_table(directory, "user_parameters")
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
        with time("Learning values", logger):
            values = self.compute_values(init, *args)
        with time("Learning uncertainties", logger):
            left_uncertainties, right_uncertainties = self.compute_uncertainties(values, *args)
        return values, left_uncertainties, right_uncertainties
    
    def compute_values(self, init: NDArray, *args) -> NDArray:
        """ Computes the values given comparisons by minimizing a loss function, using gradients and/or partial derivatives """
        return self.minimizer(init, args, self.loss, self.gradient, self.partial_derivatives_getter)

    def compute_uncertainties(self, values: NDArray, *args) -> tuple[NDArray, NDArray]:
        """ Given learned maximum-a-posteriori values, determines uncertainties """
        return self.uncertainty(values, args, self.cw_prior_loss_getter, self.cw_nll_loss_getter, self.hess_diagonal)
    
    #################################################################
    ## Derived methods. They could be optimized in derived classes ##
    #################################################################

    def partial_derivatives_getter(self, 
        value_index: int, 
        values: NDArray, 
        *args: Any
    ) -> Callable[[float, *tuple[Any, ...]], float]:
        def derivative(value: float, *derivative_args: Any) -> float:
            old_value = values[value_index]
            values[value_index] = value
            gradient = self.gradient(values, *derivative_args)[value_index]
            values[value_index] = old_value
            return gradient
        return derivative

    def loss(self, values: NDArray[np.float64], *args) -> float:
        return self.prior_loss(values, *args) + self.nll(values, *args)

    def nll(self, values: NDArray[np.float64], *args) -> float:
        return self.nlls(values, *args).sum()

    def cw_prior_loss_getter(self, 
        values: NDArray[np.float64], 
        *args: Any
    ) -> tuple[Callable[[float, np.int64, *tuple[Any, ...]], float], tuple[Any, ...]]:
        def cw_prior_loss(delta: float, value_index: np.int64, *f_args) -> float:
            base_vector = np.zeros_like(values)
            base_vector[value_index] = 1
            return self.prior_loss(values + delta * base_vector, *f_args)
        return cw_prior_loss, args
    
    def cw_nll_loss_getter(self, 
        values: NDArray[np.float64], 
        *args: Any
    ) -> tuple[Callable[[float, np.int64, *tuple[Any, ...]], float], tuple[Any, ...]]:
        def cw_nll(delta: float, value_index: np.int64, *args) -> float:
            base_vector = np.zeros_like(values)
            base_vector[value_index] = 1
            return self.nlls(values + delta * base_vector, *args).sum()
        return cw_nll, args