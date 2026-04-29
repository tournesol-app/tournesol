import itertools
from typing import Any, Callable
from numpy.typing import NDArray
from numba import njit

import numpy as np

from solidago.poll import *

from solidago.poll_functions.preference_learning.parallelized import ParallelizedPreferenceLearning
from solidago.poll_functions.preference_learning.gbt.root_law import RootLaw, BradleyTerry, Uniform, Gaussian, Discrete
from solidago.primitives.datastructure.filtered_table import FilteredTable
from solidago.primitives.minimizer.minimizer import Minimizer
from solidago.primitives.similarity import Similarity
from solidago.primitives.uncertainty.uncertainty_evaluator import UncertaintyEvaluator


# We define these root law functions directly here so that they can be used in njit functions below
# (this allows to bypass the call to classes, which is not straightforward to njit)
bt_cgf = BradleyTerry.cgf
unif_cgf = Uniform.cgf
gauss_cgf = Gaussian.cgf
discrete_cgf = Discrete.cgf

bt_cgf1 = BradleyTerry.cgf1
unif_cgf1 = Uniform.cgf1
gauss_cgf1 = Gaussian.cgf1
discrete_cgf1 = Discrete.cgf1

bt_cgf2 = BradleyTerry.cgf2
unif_cgf2 = Uniform.cgf2
gauss_cgf2 = Gaussian.cgf2
discrete_cgf2 = Discrete.cgf2

ComparisonType = tuple[
    tuple[NDArray[np.int64], NDArray[np.int64], NDArray[np.float64]], # Bradley-Terry
    tuple[NDArray[np.int64], NDArray[np.int64], NDArray[np.float64]], # Uniform
    tuple[NDArray[np.int64], NDArray[np.int64], NDArray[np.float64], NDArray[np.float64]], # Gaussian
    tuple[NDArray[np.int64], NDArray[np.int64], NDArray[np.float64], NDArray[np.int64]], # Discrete
]


class FlexibleGeneralizedBradleyTerry(ParallelizedPreferenceLearning):
    root_law_names: list[str] = ["BradleyTerry", "Uniform", "Gaussian", "Discrete"]

    def __init__(self, 
        max_workers: int = 1,
        direct: bool = True,
        categories: list[str] | None = None,
        n_parameters: int = 0,
        prior_stds: dict[str, float] | None = None, # Must specify priors for directs/thresholds/categories/parameters
        entity_similarity: Similarity | tuple[str, dict] | None = None,
        minimizer: Minimizer | tuple[str, dict] | None = None,
        uncertainty: UncertaintyEvaluator | tuple[str, dict] | None = None,
        rating_root_law: str | tuple[str | None, Any] = (None, ()),
        comparison_root_law: str | tuple[str | None, Any] = (None, ()),
        discard_ratings: bool = False,
    ):
        """ Flexible Generalized Bradley Terry is a preference learning model 
        for various forms of ratings and comparisons"""
        super().__init__(max_workers, direct, categories, n_parameters, minimizer, uncertainty)
        self.prior_stds = prior_stds or dict()
        for key in ("directs", "thresholds", "categories", "parameters"):
            if not key in self.prior_stds:
                self.prior_stds[key] = 7.0
        import solidago
        self.entity_similarity = None
        if entity_similarity is not None:
            self.entity_similarity = solidago.load(entity_similarity, solidago.similarity, Similarity)
        def to_tuple(x: str | tuple) -> tuple: 
            return (x, ()) if isinstance(x, str) else x
        self.rating_root_law = to_tuple(rating_root_law)
        self.comparison_root_law = to_tuple(comparison_root_law)
        self.discard_ratings = discard_ratings

    #######################
    ##  Data management  ##
    #######################
    
    def _process_kwargs(self): # type: ignore
        return dict(ratings=Ratings()) if self.discard_ratings else dict()
    
    def _get_root_law_index(self, root_law_name: str) -> int:
        return self.root_law_names.index(root_law_name)

    def _rating_arg(self,  # type: ignore
        ratings: Ratings, 
        entities: Entities, 
        rating_contexts: list[str],
    ) -> tuple[list[np.int64], list[int], list[float], list[int], list[int | float | None]]:
        """ Ratings are ignored """
        assert not (self.discard_ratings and ratings), (self.discard_ratings, ratings)
        entity_indices = [entities.name2index(r["entity_name"]) for r in ratings]
        context_indices = [len(entities) + rating_contexts.index(r["context"]) for r in ratings]
        root_laws, root_law_indices, root_law_args = self._get_root_laws(ratings, *self.rating_root_law)
        normalized_ratings = [root_law.normalize_rating(r) for r, root_law in zip(ratings, root_laws)]
        return entity_indices, context_indices, normalized_ratings, root_law_indices, root_law_args
    
    def _comparison_arg(self,  # type: ignore
        comparisons: Comparisons, 
        entities: Entities
    ) -> tuple[list[np.int64], list[np.int64], list[float], list[int], list[int | float | None]]:
        lefts = [entities.name2index(c["left_name"]) for c in comparisons]
        rights = [entities.name2index(c["right_name"]) for c in comparisons]
        root_laws, root_law_indices, root_law_args = self._get_root_laws(comparisons, *self.comparison_root_law)
        normalized_comparisons = [r.normalize_comparison(c) for c, r in zip(comparisons, root_laws)]
        return lefts, rights, normalized_comparisons, root_law_indices, root_law_args
    
    def _get_root_laws(self,
        table: FilteredTable, 
        default_root_law_name: str | None = None, 
        default_arg: tuple = (),
    ) -> tuple[list[RootLaw], list[int], list[Any]]: # root_law_indices, root_law_args
        import solidago, solidago.poll_functions.preference_learning.gbt.root_law as m
        root_laws, indices, args = list(), list(), list()
        default_index = None if default_root_law_name is None else self.root_law_names.index(default_root_law_name)
        for row in table:
            if "root_law" not in row or row["root_law"] is None or np.isnan(row["root_law"]):
                assert default_index is not None
                index, arg = default_index, default_arg
            else:
                index = self.root_law_names.index(row["root_law"])
                arg = row["root_law_arg"] if "root_law_arg" in row else ()
            indices.append(index)
            args.append(arg)
            root_law_arg = arg if isinstance(arg, tuple) else (arg,)
            root_law = solidago.load(self.root_law_names[index], m, RootLaw, None, *root_law_arg)
            root_laws.append(root_law)
        return root_laws, indices, args

    def _args(self,  # type: ignore
        variable: tuple[User, str], 
        nonargs, # entities, category_groups, rating_contexts: tuple[Entities, list[tuple[str, list[str]]], list[str]], 
        ratings: Ratings,
        comparisons: Comparisons,
        user_models: UserModels,
    ) -> tuple[
        NDArray[np.float64], # init_value
        NDArray[np.float64], # prior_inv_vars
        NDArray[np.float64] | None, # diffusion_prior_matrix
        ComparisonType, # comparisons
        NDArray[np.int64], # category_indices
        NDArray[np.float64], # embedding_matrix
        tuple[bool, np.int64, np.int64, NDArray[np.int64], np.int64] 
        # values_args = direct, n_entities, n_thresholds, category_group_lengths, parameters_offset
    ]:
        """ Reduces ratings to comparisons. Also, drops the last unused argument `n_parameters`. """
        assert not (self.discard_ratings and ratings), (self.discard_ratings, ratings)
        args = super()._args(variable, nonargs, ratings, comparisons, user_models)
        (init_value, a, c, embedding_matrix, category_indices, direct, 
            n_entities, n_thresholds, category_group_lengths, n_parameters) = args
        comparisons_lists = (
            (list(), list(), list()), # BradleyTerry
            (list(), list(), list()), # Uniform
            (list(), list(), list(), list()), # Gaussian
            (list(), list(), list(), list()), # Discrete
        )
        comparison_args = a[0] + c[0], a[1] + c[1], a[2] + c[2], a[3] + c[3], a[4] + c[4] # type: ignore
        for left, right, comparison_value, root_law_index, root_law_arg in zip(*comparison_args):
            comparisons_lists[root_law_index][0].append(left)
            comparisons_lists[root_law_index][1].append(right)
            comparisons_lists[root_law_index][2].append(comparison_value)
            if root_law_index in range(2, 4):
                comparisons_lists[root_law_index][3].append(root_law_arg)
        np_comparisons = (
            (
                np.array(comparisons_lists[0][0], dtype=np.int64),
                np.array(comparisons_lists[0][1], dtype=np.int64),
                np.array(comparisons_lists[0][2], dtype=np.float64),
            ),
            (
                np.array(comparisons_lists[1][0], dtype=np.int64),
                np.array(comparisons_lists[1][1], dtype=np.int64),
                np.array(comparisons_lists[1][2], dtype=np.float64),
            ),
            (
                np.array(comparisons_lists[2][0], dtype=np.int64),
                np.array(comparisons_lists[2][1], dtype=np.int64),
                np.array(comparisons_lists[2][2], dtype=np.float64),
                np.array(comparisons_lists[2][3], dtype=np.float64),
            ),
            (
                np.array(comparisons_lists[3][0], dtype=np.int64),
                np.array(comparisons_lists[3][1], dtype=np.int64),
                np.array(comparisons_lists[3][2], dtype=np.float64),
                np.array(comparisons_lists[3][3], dtype=np.int64),
            ),
        )
        
        offset = n_entities if direct else 0
        prior_inv_vars = [1.0 / self.prior_stds["directs"]**2] * offset
        prior_inv_vars += [1.0 / self.prior_stds["thresholds"]**2] * n_thresholds
        prior_inv_vars += [1.0 / self.prior_stds["categories"]**2] * sum(len for len in category_group_lengths)
        prior_inv_vars += [1.0 / self.prior_stds["categories"]**2] * n_parameters
        prior_inv_vars = np.array(prior_inv_vars, dtype=np.float64)

        parameters_offset = n_thresholds + (n_entities if self.direct else 0)
        parameters_offset += sum(length for length in category_group_lengths)
        
        diffusion_prior_matrix = None
        if self.entity_similarity:
            entities, _, _ = nonargs
            # Note that we do not enter the Laplacian matrix L of the paper
            # diffusion_prior_matrix only has the nondiagonal elements
            # and register them all as positives (their absolute values in L)
            diffusion_prior_matrix = np.array([
                [0. if e.name == f.name else self.entity_similarity(e, f)] 
                for (e, f) in itertools.product(entities, entities)
            ], dtype=np.float64)
        
        return (
            init_value, prior_inv_vars, diffusion_prior_matrix,
            np_comparisons, category_indices, embedding_matrix, 
            (direct, n_entities, n_thresholds, category_group_lengths, np.int64(parameters_offset))
        )
        
    ##########################################
    ##  Key functions constructed with cgf  ##
    ##########################################

    @staticmethod
    @njit
    def njit_scores(
        values: NDArray[np.float64],
        embedding_matrix: NDArray[np.float64], # shape (len(entities), self.n_parameters) 
        category_indices: NDArray[np.int64], # shape (len(entities), len(category_list))
        values_args: tuple[bool, np.int64, np.int64, NDArray[np.int64], np.int64],
    ) -> NDArray[np.float64]:
        direct, n_entities, n_thresholds, category_group_lengths, parameters_offset = values_args
        assert isinstance(n_entities, int), n_entities
        assert isinstance(n_thresholds, int), n_thresholds
        assert isinstance(direct, bool), direct
        scores = np.zeros(n_entities + n_thresholds)
        if direct:
            scores += values[:n_entities]
        else:
            scores[n_entities:] = values[:n_thresholds]
        for category_index in range(len(category_group_lengths)):
            scores[:n_entities] += values[category_indices[:, category_index]]
        scores[:n_entities] += embedding_matrix @ values[parameters_offset:]
        return scores
    @staticmethod
    @njit
    def njit_score_partial_derivative(
        value_index: np.int64,
        embedding_matrix: NDArray[np.float64], # shape (len(entities), self.n_parameters) 
        category_indices: NDArray[np.int64], # shape (len(entities), len(category_list))
        values_args: tuple[bool, np.int64, np.int64, NDArray[np.int64], np.int64],
    ) -> NDArray[np.float64]:
        """ Given that the scores are a linear function of the values,
        the scores are a function of the values and of the partial derivatives.
        This method is especially useful to measure loss increases given a variation
        of a coordinate value """
        direct, n_entities, n_thresholds, category_group_lengths, parameters_offset = values_args
        scores = np.zeros(n_entities + n_thresholds)
        if direct and value_index < n_entities + n_thresholds:
            scores[value_index] = 1
            return scores
        if value_index < n_thresholds and not direct:
            scores[value_index] = 1
            return scores
        offset = n_thresholds + (n_entities if direct else 0)
        for category_index, category_group_length in enumerate(category_group_lengths):
            if value_index < offset + category_group_length:
                for entity_index in range(n_entities):
                    if category_indices[entity_index, category_index] == value_index:
                        scores[entity_index] += 1
                return scores
            offset += category_group_length
        scores[:n_entities] += embedding_matrix[:, value_index - parameters_offset]
        return scores
    
    def prior_loss(self,  # type: ignore
        values: NDArray[np.float64], 
        prior_inv_vars: NDArray[np.float64],
        diffusion_prior_matrix: NDArray[np.float64] | None,
        comparisons: ComparisonType, # not used
        category_indices: NDArray[np.int64], # not used
        embedding_matrix: NDArray[np.float64], # not used
        values_args: tuple[bool, np.int64, np.int64, NDArray[np.int64], np.int64], # not used
    ) -> float:
        return type(self).njit_prior_loss(values, prior_inv_vars, diffusion_prior_matrix)
    @staticmethod
    @njit
    def njit_prior_loss(
        values: NDArray[np.float64], 
        prior_inv_vars: NDArray[np.float64],
        diffusion_prior_matrix: NDArray[np.float64] | None, # not used
    ) -> float:
        prior = (prior_inv_vars * values**2).sum() / 2
        if diffusion_prior_matrix is None:
            return prior
        n_entities = len(diffusion_prior_matrix)
        for e in range(n_entities):
            for f in range(e + 1, n_entities):
                prior += diffusion_prior_matrix[e, f] * (values[e] - values[f])**2
        return prior
    
    def nlls(self,  # type: ignore
        values: NDArray[np.float64], 
        prior_inv_vars: NDArray[np.float64], # not used
        diffusion_prior_matrix: NDArray[np.float64] | None, # not used
        comparisons: ComparisonType,
        category_indices: NDArray[np.int64],
        embedding_matrix: NDArray[np.float64],
        values_args: tuple[bool, np.int64, np.int64, NDArray[np.int64], np.int64],
    ) -> NDArray:
        scores = type(self).njit_scores(values, embedding_matrix, category_indices, values_args)
        return type(self).njit_nlls(scores, comparisons)
    @staticmethod
    @njit
    def njit_nlls(scores: NDArray[np.float64], comparisons: ComparisonType) -> NDArray[np.float64]:
        bt_comparisons, unif_comparisons, gauss_comparisons, discrete_comparisons = comparisons
        bt_lefts, bt_rights, bt_values = bt_comparisons
        unif_lefts, unif_rights, unif_values = unif_comparisons
        gauss_lefts, gauss_rights, gauss_values, gauss_args = gauss_comparisons
        discrete_lefts, discrete_rights, discrete_values, discrete_args = discrete_comparisons
        n_comparisons = len(bt_lefts) + len(unif_lefts) + len(gauss_lefts) + len(discrete_lefts)
        
        nlls = np.empty(n_comparisons)
        score_diffs = scores[bt_lefts] - scores[bt_rights]
        nlls[:len(bt_lefts)] = score_diffs * bt_values + bt_cgf(score_diffs)
        offset = len(bt_lefts)

        score_diffs = scores[unif_lefts] - scores[unif_rights]
        nlls[offset:offset + len(unif_lefts)] = score_diffs * unif_values + unif_cgf(score_diffs)
        offset += len(unif_lefts)

        score_diffs = scores[gauss_lefts] - scores[gauss_rights]
        nlls[offset:offset + len(gauss_lefts)] = score_diffs * gauss_values + gauss_cgf(score_diffs, gauss_args)
        offset += len(gauss_lefts)

        score_diffs = scores[discrete_lefts] - scores[discrete_rights]
        nlls[offset:] = score_diffs * discrete_values + discrete_cgf(score_diffs, discrete_args)

        return nlls

    def gradient(self,  # type: ignore
        values: NDArray[np.float64], 
        prior_inv_vars: NDArray[np.float64],
        diffusion_prior_matrix: NDArray[np.float64] | None,
        comparisons: ComparisonType,
        category_indices: NDArray[np.int64],
        embedding_matrix: NDArray[np.float64],
        values_args: tuple[bool, np.int64, np.int64, NDArray[np.int64], np.int64],
    ) -> NDArray[np.float64]:
        gradient = type(self).njit_prior_gradient(values, prior_inv_vars, diffusion_prior_matrix)
        args = embedding_matrix, category_indices, values_args
        scores = type(self).njit_scores(values, *args)
        gradient += type(self).njit_nll_gradient(values, scores, comparisons, *args)
        return gradient
    @staticmethod
    @njit
    def njit_prior_gradient(
        values: NDArray[np.float64], 
        prior_inv_vars: NDArray[np.float64], 
        diffusion_prior_matrix: NDArray[np.float64] | None, 
    ) -> NDArray[np.float64]:
        prior_grad = prior_inv_vars * values
        if diffusion_prior_matrix is None:
            return prior_grad
        n_entities = len(diffusion_prior_matrix)
        for e in range(n_entities):
            for f in range(e + 1, n_entities):
                derivative = 2 * diffusion_prior_matrix[e, f] * (values[e] - values[f])
                prior_grad[e] += derivative
                prior_grad[f] -= derivative
        return prior_grad
    @staticmethod
    @njit
    def njit_nll_gradient(
        values: NDArray[np.float64],
        scores: NDArray[np.float64],
        comparisons: ComparisonType, # left_index, right_index, comparison, root_law
        embedding_matrix: NDArray[np.float64], # shape (len(entities), self.n_parameters) 
        category_indices: NDArray[np.int64], # shape (len(entities), len(category_list))
        values_args: tuple[bool, np.int64, np.int64, NDArray[np.int64], np.int64],
    ) -> NDArray:
        direct, n_entities, _, category_group_lengths, parameters_offset = values_args

        bt_comparisons, unif_comparisons, gauss_comparisons, discrete_comparisons = comparisons
        bt_lefts, bt_rights, bt_values = bt_comparisons
        unif_lefts, unif_rights, unif_values = unif_comparisons
        gauss_lefts, gauss_rights, gauss_values, gauss_args = gauss_comparisons
        discrete_lefts, discrete_rights, discrete_values, discrete_args = discrete_comparisons
        n_comparisons = len(bt_lefts) + len(unif_lefts) + len(gauss_lefts) + len(discrete_lefts)
        
        lefts, rights = np.empty(n_comparisons, dtype=np.int64), np.empty(n_comparisons, dtype=np.int64)
        derivatives = np.empty(n_comparisons, dtype=np.float64)
        score_diffs = scores[bt_lefts] - scores[bt_rights]
        derivatives[:len(bt_lefts)] = bt_values + bt_cgf1(score_diffs)
        lefts[:len(bt_lefts)] = bt_lefts
        rights[:len(bt_rights)] = bt_rights
        offset = len(bt_lefts)

        score_diffs = scores[unif_lefts] - scores[unif_rights]
        derivatives[offset:offset + len(unif_lefts)] = unif_values + unif_cgf1(score_diffs)
        lefts[offset:offset + len(unif_lefts)] = unif_lefts
        rights[offset:offset + len(unif_rights)] = unif_rights
        offset += len(unif_lefts)

        score_diffs = scores[gauss_lefts] - scores[gauss_rights]
        derivatives[offset:offset + len(gauss_lefts)] = gauss_values + gauss_cgf1(score_diffs, gauss_args)
        lefts[offset:offset + len(gauss_lefts)] = gauss_lefts
        rights[offset:offset + len(gauss_rights)] = gauss_rights
        offset += len(gauss_lefts)

        score_diffs = scores[discrete_lefts] - scores[discrete_rights]
        derivatives[offset:] = score_diffs * discrete_values + discrete_cgf(score_diffs, discrete_args)
        lefts[offset:] = discrete_lefts
        rights[offset:] = discrete_rights
    
        gradient = np.zeros_like(values)
        for left, right, derivative in zip(lefts, rights, derivatives):
            if direct:
                gradient[left] += derivative
                gradient[right] -= derivative
            if (not direct) and right >= n_entities: # is an assessment
                gradient[right - n_entities] -= derivative # updates threshold
            if len(category_group_lengths) > 0:
                gradient[category_indices[left]] += derivative
                if right < n_entities: # right is an entity, not a threshold
                    gradient[category_indices[right]] -= derivative
            if len(embedding_matrix) > 0:
                if right < n_entities:
                    embedding = embedding_matrix[left] - embedding_matrix[right]
                else:
                    embedding = embedding_matrix[left]
                gradient[parameters_offset:] += derivative * embedding
        
        return gradient

    def hess_diagonal(self,  # type: ignore
        values: NDArray[np.float64], 
        prior_inv_vars: NDArray[np.float64],
        diffusion_prior_matrix: NDArray[np.float64] | None,
        comparisons: ComparisonType,
        category_indices: NDArray[np.int64],
        embedding_matrix: NDArray[np.float64],
        values_args: tuple[bool, np.int64, np.int64, NDArray[np.int64], np.int64],
    ) -> NDArray[np.float64]:
        scores = type(self).njit_scores(values, embedding_matrix, category_indices, values_args)
        return type(self).njit_hess_diagonal(values, scores, comparisons, prior_inv_vars, diffusion_prior_matrix)
    @staticmethod
    @njit
    def njit_hess_diagonal(
        values: NDArray[np.float64], 
        scores: NDArray[np.float64],
        comparisons: ComparisonType, # left_index, right_index, comparison, root_law
        prior_inv_vars: NDArray[np.float64],
        diffusion_prior_matrix: NDArray[np.float64] | None,
    ) -> NDArray[np.float64]:
        hess = prior_inv_vars.copy()
        bt_comparisons, unif_comparisons, gauss_comparisons, discrete_comparisons = comparisons
        
        bt_lefts, bt_rights, _ = bt_comparisons
        score_diffs = scores[bt_lefts] - scores[bt_rights]
        for left, right, h in zip(bt_lefts, bt_rights, bt_cgf2(score_diffs)):
            hess[[left, right]] += h

        unif_lefts, unif_rights, _ = unif_comparisons
        score_diffs = scores[unif_lefts] - scores[unif_rights]
        for left, right, h in zip(unif_lefts, unif_rights, unif_cgf2(score_diffs)):
            hess[[left, right]] += h

        gauss_lefts, gauss_rights, _, gauss_args = gauss_comparisons
        score_diffs = scores[gauss_lefts] - scores[gauss_rights]
        for left, right, h in zip(gauss_lefts, gauss_rights, gauss_cgf2(score_diffs, gauss_args)):
            hess[[left, right]] += h

        discrete_lefts, discrete_rights, _, discrete_args = discrete_comparisons
        score_diffs = scores[discrete_lefts] - scores[discrete_rights]
        for left, right, h in zip(discrete_lefts, discrete_rights, discrete_cgf2(score_diffs, discrete_args)):
            hess[[left, right]] += h

        if diffusion_prior_matrix is not None:
            hess[:len(diffusion_prior_matrix)] += diffusion_prior_matrix.sum(axis=0)

        return hess 
