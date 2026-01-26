import numpy as np
import pytest

from solidago import *
from solidago.functions.preference_learning import NumbaUniformGBT, LBFGSUniformGBT, FlexibleGeneralizedBradleyTerry
from solidago.functions.preference_learning.gbt.root_law import RootLaw, BradleyTerry, Uniform, Gaussian, Discrete


@pytest.mark.parametrize("GBT", [NumbaUniformGBT, LBFGSUniformGBT])
def test_gbt_score_zero(GBT):
    
    if GBT == LBFGSUniformGBT:
        pytest.importorskip("torch")
        
    entities=Entities(["entity_1", "entity_2", "entity_3"])
    comparisons=Comparisons(["entity_name", "other_name"])
    comparisons["entity_1", "entity_2"] = Comparison(0, 10)
    comparisons["entity_1", "entity_3"] = Comparison(0, 10)
    
    scores = GBT(max_workers=2).user_learn_criterion(entities, comparisons)
    
    assert scores["entity_1"].to_triplet() == pytest.approx((0, 1.8, 1.8), abs=0.1)
    assert scores["entity_2"].to_triplet() == pytest.approx((0, 2.7, 2.7), abs=0.1)
    assert scores["entity_3"].to_triplet() == pytest.approx((0, 2.7, 2.7), abs=0.1)
    
    
@pytest.mark.parametrize("GBT", [NumbaUniformGBT, LBFGSUniformGBT])
def test_gbt_score_monotonicity(GBT):
    
    if GBT == LBFGSUniformGBT:
        pytest.importorskip("torch")
        
    entities = Entities(["entity_1", "entity_2", "entity_3"])
    comparisons = Comparisons(["entity_name", "other_name"])
    comparisons["entity_1", "entity_2"] = Comparison(5, 10)
    comparisons["entity_1", "entity_3"] = Comparison(2, 10)
    
    scores = GBT(max_workers=2).user_learn_criterion(entities, comparisons)
    
    assert scores["entity_1"].value < scores["entity_3"].value
    assert scores["entity_3"].value < scores["entity_2"].value
    assert scores["entity_1"].left_unc > scores["entity_1"].right_unc
    assert scores["entity_2"].left_unc < scores["entity_2"].right_unc


@pytest.mark.parametrize("GBT", [NumbaUniformGBT, LBFGSUniformGBT])
def test_uniform_gbt(GBT):
    poll = Poll.load(f"tests/saved/0")
    _, _, fgbt_user_models = FlexibleGeneralizedBradleyTerry(discard_ratings=True).poll2objects_function(poll)
    _, _, gbt_user_models = GBT().poll2objects_function(poll)
    for user in poll.users:
        for entity in poll.entities:
            for criterion in poll.criteria():
                fgbt_score = fgbt_user_models[user](entity, criterion)
                gbt_score = gbt_user_models[user](entity, criterion)
                args = (str(user), str(entity), criterion, fgbt_score, gbt_score)
                if fgbt_score.isnan():
                    assert gbt_score.isnan(), args
                else:
                    assert fgbt_score.to_triplet() == pytest.approx(gbt_score.to_triplet(), abs=5e-1), args


@pytest.mark.parametrize("RootLawClass", [BradleyTerry, Uniform, Gaussian, Discrete])
def test_root_laws(RootLawClass):
    kwargs = dict()
    if RootLawClass == Gaussian:
        kwargs["std"] = 1.0
    if RootLawClass == Discrete:
        kwargs["n_values"] = 7
    r = RootLawClass(**kwargs)
    assert isinstance(r, RootLaw)
    score_diffs = np.array([0, 1, 1e-5, 100])
    assert all(np.abs(r.cgf(score_diffs) - r.cgf(score_diffs)) < 1e-3)
    assert all(r.cgf_derivative(score_diffs) >= 0)
    assert all(np.abs(r.cgf_derivative(score_diffs)) <= r.sup())
    assert all(np.abs(r.cgf_derivative(score_diffs) + r.cgf_derivative(- score_diffs)) < 1e-3)
    assert all(np.abs(r.cgf_2nd_derivative(score_diffs) - r.cgf_2nd_derivative(- score_diffs)) < 1e-3)

def test_numba():
    gbt = NumbaUniformGBT()
    poll = Poll.load(f"tests/saved/0")
    user, criterion = poll.users["user_4"], "default"
    init_model = ScoringModel()
    comparisons = poll.comparisons[user].reorder("criterion", "entity_name", "other_name")
    entities = poll.entities[comparisons[criterion].keys("entity_name")]
    assert "entity_4" in entities
    assert isinstance(entities, Entities)
    init = init_model(entities, criterion)
    values = gbt.compute_values(entities, comparisons, init)
    assert not np.isnan(values[entities.name2index("entity_4")]), values[entities.name2index("entity_4")]
    lefts, rights = gbt.compute_uncertainties(entities, comparisons, values)
    assert np.isfinite(lefts[entities.name2index("entity_4")]), values[entities.name2index("entity_4")]
    assert np.isfinite(rights[entities.name2index("entity_4")]), values[entities.name2index("entity_4")]


def test_flexible():
    n_parameters = 4
    categories = ["author", "journalism"]
    fgbt = functions.FlexibleGeneralizedBradleyTerry(
        n_parameters=n_parameters,
        categories=categories,
        rating_root_law=("Gaussian", dict(std=1.0)),
    )
    poll = Poll.load(f"tests/saved/0")
    user, criterion = poll.users["user_0"], "default"
    variable = user, criterion
    entities, user_models = poll.entities, poll.user_models
    ratings, comparisons = poll.ratings, poll.comparisons
    nonargs = fgbt._nonargs(variable, entities, ratings, comparisons)
    evaluated_entities, category_groups, rating_contexts = nonargs
    args = fgbt._args(variable, nonargs, ratings, comparisons, user_models)
    (values, extended_comparisons, prior_inv_vars, embedding_matrix, category_indices, 
        direct, n_entities, n_thresholds, category_group_lengths,
        categories_offsets, parameters_offset) = args
    left_indices, right_indices, comparison_value, root_laws = extended_comparisons
    
    assert isinstance(evaluated_entities, Entities), evaluated_entities
    assert category_groups, category_groups
    assert rating_contexts == ["undefined"], rating_contexts
    assert len(values) == len(evaluated_entities) + n_parameters + n_thresholds + sum(l for l in category_group_lengths)
    assert all(i in range(len(values)) for i in left_indices), left_indices
    assert all(i in range(len(values)) for i in right_indices), right_indices
    assert all(np.isfinite(v) for v in comparison_value), comparison_value
    assert all(isinstance(r, RootLaw) for r in root_laws), root_laws
    assert len(prior_inv_vars) == len(values) 
    assert direct, direct
    assert embedding_matrix.shape == (n_entities, n_parameters), embedding_matrix.shape
    assert categories_offsets[0] == len(evaluated_entities) + n_thresholds
    assert categories_offsets[1] == len(evaluated_entities) + n_thresholds + category_group_lengths[0]
    assert parameters_offset == len(evaluated_entities) + n_thresholds + sum(l for l in category_group_lengths)
    assert all(category_indices[:, 0] >= categories_offsets[0])
    assert all(category_indices[:, 0] < categories_offsets[1])
    assert all(category_indices[:, 1] >= categories_offsets[1])
    assert all(category_indices[:, 1] < parameters_offset)

    offset = n_thresholds + (n_entities if direct else 0)
    scores = values[:offset] if direct else np.concatenate([np.zeros(n_entities), values[:n_thresholds]])
    for category_index, _ in enumerate(category_group_lengths):
        scores[:n_entities] += values[category_indices[:, category_index]]
    scores[:n_entities] += embedding_matrix @ values[parameters_offset:]

    gradient = prior_inv_vars * values
    assert len(gradient) == len(values)
    args = direct, n_entities, n_thresholds, category_group_lengths, categories_offsets, parameters_offset
    scores = type(fgbt).virtual_entity_scores(values, embedding_matrix, category_indices, *args)
    lefts, rights, comparison_values, root_laws = extended_comparisons
    left, right, comparison_value, r = next(iter(zip(lefts, rights, comparison_values, root_laws)))
    diff_derivative = comparison_value + r.cgf_derivative(scores[left] - scores[right])
    gradient[left] += diff_derivative
    gradient[category_indices[left]] += diff_derivative
    gradient[right] -= diff_derivative
    if right < n_entities: # right is an entity, not a threshold
        gradient[category_indices[right]] -= diff_derivative
    embedding = embedding_matrix[left]
    if right < n_entities: # right is an entity, not a threshold
        embedding -= embedding_matrix[right]
    gradient[parameters_offset:] += diff_derivative * embedding

    fgbt_users, fgbt_entities, fgbt_user_models = fgbt.poll2objects_function(poll)
    assert len(fgbt_users) == len(poll.users)
    assert "rating_threshold_undefined_value" in fgbt_users["user_0"]
    assert len(fgbt_entities) == len(poll.entities)
    assert "n_raters" in fgbt_entities["entity_1"]
    assert "user_2" in fgbt_user_models.user_directs.keys("username")
    assert not user_models.user_categories["user_1", "author", "Science4All", "default"].isnan()

def test_uncertainty_comparison_only():
    fgbt = functions.FlexibleGeneralizedBradleyTerry(discard_ratings=True)
    poll = Poll.load(f"tests/saved/0")
    user, criterion = poll.users["user_0"], "default"
    variable = user, criterion
    entities, user_models = poll.entities, poll.user_models
    ratings, comparisons = Ratings(), poll.comparisons
    nonargs = fgbt._nonargs(variable, entities, ratings, comparisons)
    evaluated_entities, category_groups, rating_contexts = nonargs
    args = fgbt._args(variable, nonargs, ratings, comparisons, user_models)
    (init_values, extended_comparisons, prior_inv_vars, embedding_matrix, category_indices, 
        direct, n_entities, n_thresholds, category_group_lengths,
        categories_offsets, parameters_offset) = args
    values = fgbt.compute_values(*args)
    args = args[1:] # dropping init_values
    left_uncertainties, right_uncertainties = fgbt.compute_uncertainties(values, *args)
    assert all(np.abs(values) < 20)
    assert all(np.abs(left_uncertainties) < 20)
    assert all(np.abs(right_uncertainties) < 20)
    assert fgbt.loss(values, *args) <= 0

def test_uncertainty():
    n_parameters = 4
    categories = ["author", "journalism"]
    fgbt = functions.FlexibleGeneralizedBradleyTerry(
        n_parameters=n_parameters,
        categories=categories,
        rating_root_law=("Gaussian", dict(std=1.0)),
    )
    poll = Poll.load(f"tests/saved/0")
    user, criterion = poll.users["user_0"], "default"
    variable = user, criterion
    entities, user_models = poll.entities, poll.user_models
    ratings, comparisons = poll.ratings, poll.comparisons
    nonargs = fgbt._nonargs(variable, entities, ratings, comparisons)
    evaluated_entities, category_groups, rating_contexts = nonargs
    args = fgbt._args(variable, nonargs, ratings, comparisons, user_models)
    (init_values, extended_comparisons, prior_inv_vars, embedding_matrix, category_indices, 
        direct, n_entities, n_thresholds, category_group_lengths,
        categories_offsets, parameters_offset) = args
    values = fgbt.compute_values(*args)
    args = args[1:] # dropping init_values
    left_uncertainties, right_uncertainties = fgbt.compute_uncertainties(values, *args)
    assert all(np.abs(values) < 20)
    assert all(np.abs(left_uncertainties) < 20)
    assert all(np.abs(right_uncertainties) < 20)
    assert fgbt.loss(values, *args) <= 0