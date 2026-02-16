import numpy as np
import pytest

from solidago import *
from solidago.poll_functions.preference_learning import NumbaUniformGBT, LBFGSUniformGBT, FlexibleGeneralizedBradleyTerry
from solidago.poll_functions.preference_learning.gbt.root_law import RootLaw, BradleyTerry, Uniform, Gaussian, Discrete


@pytest.mark.parametrize("GBT", [NumbaUniformGBT, LBFGSUniformGBT])
def test_gbt_score_zero(GBT):
    
    if GBT == LBFGSUniformGBT:
        pytest.importorskip("torch")
        
    entities=Entities(["entity_1", "entity_2", "entity_3"])
    comparisons=Comparisons(keynames=["entity_name", "other_name"])
    comparisons.set(left_name="entity_1", right_name="entity_2", value=0, max=10)
    comparisons.set(left_name="entity_1", right_name="entity_3", value=0, max=10)
    
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
    comparisons.set(left_name="entity_1", right_name="entity_2", value=5, max=10)
    comparisons.set(left_name="entity_1", right_name="entity_3", value=2, max=10)
    
    scores = GBT(max_workers=2).user_learn_criterion(entities, comparisons)
    assert isinstance(scores, Scores)
    
    assert scores.get(entity_name="entity_1").value < scores.get(entity_name="entity_3").value
    assert scores.get(entity_name="entity_3").value < scores.get(entity_name="entity_2").value
    assert scores.get(entity_name="entity_1").left_unc > scores.get(entity_name="entity_1").right_unc
    assert scores.get(entity_name="entity_2").left_unc < scores.get(entity_name="entity_2").right_unc


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
    args = ()
    if RootLawClass == Gaussian:
        args = (1.,)
    if RootLawClass == Discrete:
        args = (7,)
    r = RootLawClass(*args)
    assert isinstance(r, RootLaw)
    score_diffs = np.array([0, 1, 1e-5, 100])
    assert all(np.abs(RootLawClass.cgf(score_diffs, *args) - RootLawClass.cgf(score_diffs, *args)) < 1e-3)
    assert all(RootLawClass.cgf1(score_diffs, *args) >= 0)
    assert all(np.abs(RootLawClass.cgf1(score_diffs, *args)) <= r.sup())
    assert all(np.abs(RootLawClass.cgf1(score_diffs, *args) + RootLawClass.cgf1(- score_diffs, *args)) < 1e-3)
    assert all(np.abs(RootLawClass.cgf2(score_diffs, *args) - RootLawClass.cgf2(- score_diffs, *args)) < 1e-3)

def test_numba():
    gbt = NumbaUniformGBT()
    poll = Poll.load(f"tests/saved/0")
    _, criterion = poll.users["user_4"], "default"
    init_model = ScoringModel()
    comparisons = poll.comparisons.filters(criterion=criterion)
    entities = poll.entities[list(comparisons.keys("entity_name"))]
    assert "entity_4" in entities
    assert isinstance(entities, Entities)
    init = init_model(entities, criterion)
    assert isinstance(init, Scores)
    values = gbt.compute_values(entities, poll.comparisons, init)
    assert not np.isnan(values[entities.name2index("entity_4")]), values[entities.name2index("entity_4")]
    lefts, rights = gbt.compute_uncertainties(entities, comparisons, values)
    assert np.isfinite(lefts[entities.name2index("entity_4")]), values[entities.name2index("entity_4")]
    assert np.isfinite(rights[entities.name2index("entity_4")]), values[entities.name2index("entity_4")]


def test_flexible():
    n_parameters = 4
    categories = ["author", "journalism"]
    fgbt = poll_functions.FlexibleGeneralizedBradleyTerry(
        n_parameters=n_parameters,
        categories=categories,
        rating_root_law=("Gaussian", dict(std=1.0)),
    )
    poll = Poll.load(f"tests/saved/0")
    user, criterion = poll.users["user_0"], "default"
    assert isinstance(user, User)
    variable = user, criterion
    entities, user_models = poll.entities, poll.user_models
    ratings, comparisons = poll.ratings, poll.comparisons
    nonargs = fgbt._nonargs(variable, entities, ratings, comparisons)
    evaluated_entities, category_groups, rating_contexts = nonargs
    args = fgbt._args(variable, nonargs, ratings, comparisons, user_models)
    
    values, prior_inv_vars, diffusion_prior_matrix = args[:3]
    extended_comparisons, category_indices, embedding_matrix, values_args = args[3:]
    bt_lefts, bt_rights, bt_values = extended_comparisons[0]
    unif_lefts, unif_rights, unif_values = extended_comparisons[1]
    gauss_lefts, gauss_rights, gauss_values, gauss_args = extended_comparisons[2]
    discrete_lefts, discrete_rights, discrete_values, discrete_args = extended_comparisons[3]
    direct, n_entities, n_thresholds, category_group_lengths, parameters_offset = values_args
    
    assert isinstance(evaluated_entities, Entities), evaluated_entities
    assert category_groups, category_groups
    assert rating_contexts == ["undefined"], rating_contexts
    assert len(values) == len(evaluated_entities) + n_parameters + n_thresholds + sum(l for l in category_group_lengths)
    assert all(i in range(len(values)) for i in bt_lefts), bt_lefts
    assert all(i in range(len(values)) for i in bt_rights), bt_rights
    assert all(i in range(len(values)) for i in unif_lefts), unif_lefts
    assert all(i in range(len(values)) for i in unif_rights), unif_rights
    assert all(i in range(len(values)) for i in gauss_lefts), gauss_lefts
    assert all(i in range(len(values)) for i in gauss_rights), gauss_rights
    assert all(i in range(len(values)) for i in discrete_lefts), discrete_lefts
    assert all(i in range(len(values)) for i in discrete_rights), discrete_rights
    assert all(np.isfinite(v) for v in bt_values), bt_values
    assert all(np.isfinite(v) for v in unif_values), unif_values
    assert all(np.isfinite(v) for v in gauss_values), gauss_values
    assert all(np.isfinite(v) for v in discrete_values), discrete_values
    assert all(np.isfinite(v) for v in gauss_args), gauss_args
    assert all(np.isfinite(v) for v in discrete_args), discrete_args
    assert len(prior_inv_vars) == len(values)
    assert direct, direct
    assert embedding_matrix.shape == (n_entities, n_parameters), embedding_matrix.shape
    assert parameters_offset == len(evaluated_entities) + n_thresholds + sum(l for l in category_group_lengths)
    assert all(category_indices[:, 1] < parameters_offset)
    assert diffusion_prior_matrix is None
    assert isinstance(n_entities, np.integer), n_entities
    assert isinstance(n_thresholds, np.integer), n_thresholds
    assert isinstance(direct, bool), direct

    offset = n_thresholds + (n_entities if direct else 0)
    scores = np.zeros(offset)
    if direct:
        scores += values[:offset]
    else:
        scores[n_entities:] = values[:n_thresholds]
    for category_index in range(len(category_group_lengths)):
        category_subindices = category_indices[:, category_index]
        scores[:n_entities] += values[category_subindices]
    scores[:n_entities] += embedding_matrix @ values[parameters_offset:]

    gradient = prior_inv_vars * values
    assert len(gradient) == len(values)
    scores = type(fgbt).njit_scores(values, embedding_matrix, category_indices, values_args)
    
    diff_derivatives = unif_values + Uniform.cgf1(scores[unif_lefts] - scores[unif_rights])
    left, right, diff_derivative = next(iter(zip(unif_lefts, unif_rights, diff_derivatives)))
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
    assert not user_models.user_categories.get(username="user_1", category="author", group="Science4All", criterion="default").isnan()

def test_uncertainty_comparison_only():
    fgbt = poll_functions.FlexibleGeneralizedBradleyTerry(discard_ratings=True)
    poll = Poll.load(f"tests/saved/0")
    user, criterion = poll.users["user_0"], "default"
    assert isinstance(user, User)
    variable = user, criterion
    entities, user_models = poll.entities, poll.user_models
    ratings, comparisons = Ratings(), poll.comparisons
    nonargs = fgbt._nonargs(variable, entities, ratings, comparisons)
    evaluated_entities, category_groups, rating_contexts = nonargs
    args = fgbt._args(variable, nonargs, ratings, comparisons, user_models)
    values = fgbt.compute_values(*args)
    values_copy = values.copy()
    assert all(np.abs(values) < 20)
    args = args[1:] # dropping init_values
    left_uncertainties, right_uncertainties = fgbt.compute_uncertainties(values, *args)
    assert all(values_copy == values)
    assert all(np.abs(values) < 20)
    assert fgbt.loss(values, *args) <= 0

def test_uncertainty():
    n_parameters = 4
    categories = ["author", "journalism"]
    fgbt = poll_functions.FlexibleGeneralizedBradleyTerry(
        n_parameters=n_parameters,
        categories=categories,
        rating_root_law=("Gaussian", dict(std=1.0)),
    )
    poll = Poll.load(f"tests/saved/0")
    user, criterion = poll.users["user_0"], "default"
    assert isinstance(user, User)
    variable = user, criterion
    entities, user_models = poll.entities, poll.user_models
    ratings, comparisons = poll.ratings, poll.comparisons
    nonargs = fgbt._nonargs(variable, entities, ratings, comparisons)
    evaluated_entities, category_groups, rating_contexts = nonargs
    args = fgbt._args(variable, nonargs, ratings, comparisons, user_models)
    values = fgbt.compute_values(*args)
    assert all(np.abs(values) < 10)
    values_copy = values.copy()
    args = args[1:] # dropping init_values
    left_uncertainties, right_uncertainties = fgbt.compute_uncertainties(values, *args)
    assert all(values_copy == values)
    assert all(np.abs(values) < 10)
    assert fgbt.loss(values, *args) <= 0