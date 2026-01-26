from abc import abstractmethod
from copy import deepcopy
from typing import Callable
from numpy.typing import NDArray

import numpy as np

from solidago.poll import *

from solidago.functions.preference_learning.parallelized import ParallelizedPreferenceLearning
from solidago.functions.preference_learning.gbt.root_law import RootLaw


class FlexibleGeneralizedBradleyTerry(ParallelizedPreferenceLearning):
    def __init__(self, 
        max_workers: int = 1,
        direct: bool = True,
        categories: list[str] | None = None,
        n_parameters: int = 0,
        prior_stds: dict[str, float] | None = None, # Must specify priors for directs/thresholds/categories/parameters
        minimizer: tuple[str, dict] | None = None,
        uncertainty: tuple[str, dict] | None = None,
        rating_root_law: tuple[str, dict | None] | None = ("Uniform", None),
        comparison_root_law: tuple[str, dict | None] | None = ("Uniform", None),
        discard_ratings: bool = False,
    ):
        """ Flexible Generalized Bradley Terry is a preference learning model 
        for various forms of ratings and comparisons"""
        super().__init__(max_workers, direct, categories, n_parameters, minimizer, uncertainty)
        self.prior_stds = prior_stds or dict()
        for key in ("directs", "thresholds", "categories", "parameters"):
            if not key in self.prior_stds:
                self.prior_stds[key] = 7.0
        self.rating_root_law = None if rating_root_law is None else RootLaw.load(rating_root_law)
        self.comparison_root_law = None if comparison_root_law is None else RootLaw.load(comparison_root_law)
        self.discard_ratings = discard_ratings

    #######################
    ##  Data management  ##
    #######################
    
    def _process_kwargs(self):
        return dict(ratings=Ratings()) if self.discard_ratings else dict()
    
    def _rating_arg(self, 
        ratings: Ratings, 
        entities: Entities, 
        rating_contexts: list[str]
    ) -> tuple[NDArray, NDArray, list[RootLaw], NDArray]:
        """ Ratings are ignored """
        assert not (self.discard_ratings and ratings), (self.discard_ratings, ratings)
        entity_indices = np.array([entities.name2index(entity_name) for (entity_name,), _ in ratings], dtype=np.int64)
        root_laws = [RootLaw.load(a.root_law, self.rating_root_law) for _, a in ratings]
        normalized_ratings = np.array([r.normalize_rating(a) for (_, a), r in zip(ratings, root_laws)]) - 1
        context_indices = np.array([len(entities) + rating_contexts.index(a.context) for _, a in ratings], dtype=np.int64)
        return entity_indices, context_indices, normalized_ratings, root_laws
    
    def _comparison_arg(self, comparisons: Comparisons, entities: Entities) -> tuple[NDArray, NDArray, NDArray, list[RootLaw]]: 
        lefts = np.array([entities.name2index(l) for (l, _), _ in comparisons.left_right_iter()], dtype=np.int64)
        rights = np.array([entities.name2index(r) for (_, r), _ in comparisons.left_right_iter()], dtype=np.int64)
        root_laws = [RootLaw.load(c.root_law, self.comparison_root_law) for _, c in comparisons]
        normalized_comparisons = np.array([
            r.normalize_comparison(c)
            for (_, c), r in zip(comparisons.left_right_iter(), root_laws)
        ], dtype=np.float64)
        return lefts, rights, normalized_comparisons, root_laws

    def _args(self, 
        variable: tuple[User, str], 
        nonargs, # tuple[Entities, list[tuple[str, list[str]]], list[str]], 
        ratings: Ratings,
        comparisons: Comparisons,
        user_models: UserModels,
    ) -> list[NDArray, tuple[NDArray, NDArray, NDArray, list[RootLaw]], NDArray, NDArray, bool, int, NDArray]:
        """ Reduces ratings to comparisons. Also, drops the last unused argument `n_parameters`. """
        assert not (self.discard_ratings and ratings), (self.discard_ratings, ratings)
        args = super()._args(variable, nonargs, ratings, comparisons, user_models)
        init_value, a, c, embedding_matrix, category_indices, direct, n_entities, n_thresholds, category_group_lengths, n_parameters = args
        extended_comparisons = np.concatenate([a[0], c[0]]), np.concatenate([a[1], c[1]]), np.concatenate([a[2], c[2]]), a[3] + c[3]
        
        offset = n_entities if direct else 0
        prior_inv_vars = [1.0 / self.prior_stds["directs"]**2] * offset
        prior_inv_vars += [1.0 / self.prior_stds["thresholds"]**2] * n_thresholds
        prior_inv_vars += [1.0 / self.prior_stds["categories"]**2] * sum(len for len in category_group_lengths)
        prior_inv_vars += [1.0 / self.prior_stds["categories"]**2] * n_parameters
        prior_inv_vars = np.array(prior_inv_vars)

        offset = n_thresholds + (n_entities if self.direct else 0)
        categories_offsets = list()
        for length in category_group_lengths:
            categories_offsets.append(offset)
            offset += length
        parameters_offset = offset
        
        return (
            init_value, extended_comparisons, prior_inv_vars, 
            embedding_matrix, category_indices, 
            direct, n_entities, n_thresholds, category_group_lengths,
            np.array(categories_offsets), parameters_offset
        )
        
    ##########################################
    ##  Key functions constructed with cgf  ##
    ##########################################

    # @njit
    def virtual_entity_scores(
        values: NDArray,
        embedding_matrix: NDArray, # shape (len(entities), self.n_parameters) 
        category_indices: NDArray, # shape (len(entities), len(category_list))
        direct: bool,
        n_entities: int,
        n_thresholds: int,
        category_group_lengths: NDArray, # shape (len(category_list),) with int values
        categories_offsets: NDArray, # not used
        parameters_offset: int
    ) -> NDArray:
        assert isinstance(n_entities, int), n_entities
        assert isinstance(n_thresholds, int), n_thresholds
        assert isinstance(direct, bool), direct
        offset = n_thresholds + (n_entities if direct else 0)
        scores = deepcopy(values[:offset]) if direct else np.concatenate([np.zeros(n_entities), values[:n_thresholds]])
        for category_index, _ in enumerate(category_group_lengths):
            scores[:n_entities] += values[category_indices[:, category_index]]
        scores[:n_entities] += embedding_matrix @ values[parameters_offset:]
        return scores
        
    def prior_loss(self, values: NDArray, *args) -> float:
        return (args[1] * values**2).sum() / 2 # args[1] must be prior_inv_vars
    
    def nlls(self,
        values: NDArray, 
        comparisons: tuple[NDArray, NDArray, NDArray, list[RootLaw]], # left_index, right_index, comparison, root_law
        prior_inv_vars: NDArray,
        *args # args used to parse values vector
    ) -> NDArray:
        scores = type(self).virtual_entity_scores(values, *args)
        lefts, rights, comparison_values, root_laws = comparisons
        score_diffs = scores[lefts] - scores[rights]
        return score_diffs * comparison_values + np.array([r.cgf(s) for s, r in zip(score_diffs, root_laws)])
    
    def gradient(self, 
        values: NDArray, 
        comparisons: tuple[NDArray, NDArray, NDArray, list[RootLaw]], # left_index, right_index, comparison, root_law
        prior_inv_vars: NDArray,
        embedding_matrix: NDArray, # shape (len(entities), self.n_parameters) 
        category_indices: NDArray, # shape (len(entities), len(category_list))
        direct: bool,
        n_entities: int,
        n_thresholds: int,
        category_group_lengths: NDArray, # shape (len(category_list),) with int values
        categories_offsets: NDArray, # not used
        parameters_offset: int
    ) -> NDArray:
        gradient = prior_inv_vars * values
        args = direct, n_entities, n_thresholds, category_group_lengths, categories_offsets, parameters_offset
        scores = type(self).virtual_entity_scores(values, embedding_matrix, category_indices, *args)
        lefts, rights, comparison_values, root_laws = comparisons
        score_diffs = scores[lefts] - scores[rights]
        for left, right, comparison_value, s, r in zip(lefts, rights, comparison_values, score_diffs, root_laws):
            diff_derivative = comparison_value + r.cgf_derivative(s)
            gradient[left] += diff_derivative
            gradient[right] -= diff_derivative
            if len(category_group_lengths) > 0:
                gradient[category_indices[left]] += diff_derivative
                if right < n_entities: # right is an entity, not a threshold
                    gradient[category_indices[right]] -= diff_derivative
            if len(embedding_matrix) > 0:
                embedding = embedding_matrix[left] - (0 if right >= n_entities else embedding_matrix[right])
                gradient[parameters_offset:] += diff_derivative * embedding
        return gradient

    def translated_prior(self, value_index: int, values: NDArray, 
        comparisons: tuple[NDArray, NDArray, NDArray, list[RootLaw]], # left_index, right_index, comparison, root_law
        prior_inv_vars: NDArray,
        *args
    ) -> Callable[[float], float]:
        def f(delta: float) -> float:
            return (values[value_index] + delta)**2 * prior_inv_vars[value_index] / 2
        return f

    def hess_diagonal(self, 
        values: NDArray, 
        comparisons: tuple[NDArray, NDArray, NDArray, list[RootLaw]], # left_index, right_index, comparison, root_law
        prior_inv_vars: NDArray,
        embedding_matrix: NDArray, # shape (len(entities), self.n_parameters) 
        category_indices: NDArray, # shape (len(entities), len(category_list))
        *args
    ) -> NDArray:
        nll_hess = np.zeros(values.shape)
        scores = type(self).virtual_entity_scores(values, embedding_matrix, category_indices, *args)
        lefts, rights, _, root_laws = comparisons
        score_diffs = scores[lefts] - scores[rights]
        for left, right, score_diff, r in zip(lefts, rights, score_diffs, root_laws):
            hess = r.cgf_2nd_derivative(np.array([score_diff]))
            nll_hess[left] += hess
            nll_hess[right] += hess
        return prior_inv_vars + nll_hess
