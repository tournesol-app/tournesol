import pytest, numpy as np
from pathlib import Path

from solidago import *

N_SEEDS = 3


def test_generate_and_save():
    generator = load("tests/generators/test_generator.yaml")
    assert isinstance(generator, Generator)

    pipeline = load("tests/save_load/pipeline.yaml", max_workers=1)
    assert isinstance(pipeline, Sequential)

    for seed in range(N_SEEDS):
        path = Path(f"tests/save_load/saved/{seed}")
        if path.is_dir():
            for f in path.iterdir():
                if f.is_file():
                    f.unlink()
        generator.seed = seed
        generator().save(f"tests/save_load/saved/{seed}")
        pipeline.seed = seed
        directory = f"tests/save_load/saved/{seed}"
        poll = Poll.load(directory)
        pipeline(poll, directory)


def test_pipeline_generated_data():
    pipeline = load("tests/save_load/pipeline.yaml", max_workers=1)
    assert isinstance(pipeline, Sequential)
    pipeline(Poll.load("tests/save_load/saved/0"))

@pytest.mark.parametrize( "seed", list(range(N_SEEDS)) )
def test_average(seed):
    poll = Poll.load(f"tests/save_load/saved/{seed}")
    _ = poll_functions.Average(max_workers=1).poll2objects_function(poll)

@pytest.mark.parametrize( "seed", list(range(N_SEEDS)) )
def test_aggregation(seed):
    poll = Poll.load(f"tests/save_load/saved/{seed}")
    aggregator = poll_functions.EntitywiseQrQuantile(quantile=0.2, lipschitz=0.1, error=1e-5, max_workers=1)
    _ = aggregator.poll2objects_function(poll)

def test_uncertainty_comparison_only():
    fgbt = poll_functions.FlexibleGeneralizedBradleyTerry(
        discard_ratings=True,
        rating_root_law=("Gaussian", 1.),
        comparison_root_law="Uniform",
    )
    poll = Poll.load(f"tests/save_load/saved/0")
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
    left_uncs, right_uncs = fgbt.compute_uncertainties(values, *args)
    assert all(values_copy == values)
    assert all(np.abs(values) < 20)
    assert fgbt.loss(values, *args) <= 0
    assert all(left_uncs >= 0)
    assert all(right_uncs >= 0)

def test_uncertainty():
    n_parameters = 4
    categories = ["author", "journalism"]
    fgbt = poll_functions.FlexibleGeneralizedBradleyTerry(
        n_parameters=n_parameters,
        categories=categories,
        rating_root_law=("Gaussian", 1.0),
        comparison_root_law="Uniform",
    )
    poll = Poll.load(f"tests/save_load/saved/0")
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
    left_uncs, right_uncs = fgbt.compute_uncertainties(values, *args)
    assert all(values_copy == values)
    assert all(np.abs(values) < 10)
    assert fgbt.loss(values, *args) <= 0
    assert all(left_uncs >= 0)
    assert all(right_uncs >= 0)

@pytest.mark.parametrize("seed", range(N_SEEDS))
def test_learned_models(seed):
    poll = Poll.load(f"tests/save_load/saved/{seed}")
    base_models = UserModels(user_directs=poll.user_models.user_directs)
    scaled_users, scaled = poll_functions.Mehestan()(poll.users, poll.entities, poll.public_settings, base_models)
    assert len(scaled_users) == len(poll.users)
    assert len(base_models) == len(scaled)

@pytest.mark.parametrize("seed", range(N_SEEDS))
def test_standardize(seed):
    poll = Poll.load(f"tests/save_load/saved/{seed}")
    base_models = UserModels(user_directs=poll.user_models.user_directs)
    standardized_models = poll_functions.LipschitzStandardize(lipschitz=1000)(poll.entities, base_models)
    values = standardized_models().value
    deviations = np.abs(values - np.median(values))
    quantile = int(0.9 * len(deviations))
    assert deviations[np.argsort(deviations)[quantile]] < 3
    assert deviations[np.argsort(deviations)[quantile]] > 0.5
    
@pytest.mark.parametrize("seed", range(N_SEEDS))
def test_quantile_shift(seed):
    poll = Poll.load(f"tests/save_load/saved/{seed}")
    quantile_shift = poll_functions.LipschitzQuantileShift(lipschitz=1000)
    base_models = UserModels(user_directs=poll.user_models.user_directs)
    shifted_models = quantile_shift(poll.entities, base_models)
    assert np.median(shifted_models().value) > 0

@pytest.mark.parametrize("seed", range(N_SEEDS))
def test_lipschitrust_generative(seed):
    poll = Poll.load(f"tests/save_load/saved/{seed}")
    trust_propagator = poll_functions.LipschiTrust(pretrust_value=0.8, decay=0.8, sink_vouch=5.0, error=1e-8,)

    users = trust_propagator(poll.users, poll.vouches)
    for user in users:
        assert user["trustworthy"] or (user["trust"] == 0)

@pytest.mark.parametrize("seed", range(N_SEEDS))
def test_lipschitrust_test_data(seed):
    poll = Poll.load(f"tests/save_load/saved/{seed}")
    pipeline = load("tests/save_load/pipeline.yaml")
    assert isinstance(pipeline, Sequential)
    users = pipeline.subfunctions[0](poll.users, poll.vouches)
    for user in users:
        assert user["trustworthy"] or (user["trust"] == 0)

@pytest.mark.parametrize("seed", range(N_SEEDS))
def test_is_trust(seed):
    poll = Poll.load(f"tests/save_load/saved/{seed}")
    voting_rights = poll_functions.Trust2VotingRights().poll2objects_function(poll)
    for vr in voting_rights:
        if poll.public_settings.get(username=vr["username"], entity_name=vr["entity_name"]):
            assert vr["voting_right"] == poll.users[vr["username"]]["trust"]
        else:
            assert vr["voting_right"] == 0.5 * poll.users[vr["username"]]["trust"] # type: ignore

@pytest.mark.parametrize("seed", range(N_SEEDS))
def test_affine_overtrust_test_data(seed):
    poll = Poll.load(f"tests/save_load/saved/{seed}")
    ao = poll_functions.AffineOvertrust(privacy_penalty=0.5, min_overtrust=2.0, overtrust_ratio=0.1, max_workers=1)
    _, voting_rights = ao.poll2objects_function(poll)
    for voting_right in voting_rights:
        assert voting_right["voting_right"] >= 0
