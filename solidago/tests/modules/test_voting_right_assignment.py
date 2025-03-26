import pytest
import numpy as np
import pandas as pd

from solidago import *
from solidago.modules.voting_rights import Trust2VotingRights, AffineOvertrust


states = [ State.load(f"tests/saved/{seed}") for seed in range(5) ]

@pytest.mark.parametrize("seed", range(4))
def test_is_trust(seed):
    voting_rights = Trust2VotingRights().state2objects_function(states[seed])
    for (username, entity_name, criterion), voting_right in voting_rights:
        if states[seed].made_public.get(username, entity_name):
            assert voting_right == states[seed].users.get(username)["trust_score"]
        else:
            assert voting_right == 0.5 * states[seed].users.get(username)["trust_score"]


ao = AffineOvertrust(privacy_penalty=0.5, min_overtrust=2.0, overtrust_ratio=0.1)

def test_empty_input():
    np.testing.assert_array_equal(
        ao.computing_voting_rights_and_statistics(
            np.array([]), 
            np.array([])
        )[0], []
    )

def test_everyone_trusted():
    np.testing.assert_array_equal(
        ao.computing_voting_rights_and_statistics(
            np.array([1, 1, 1, 1]), 
            np.ones(shape=4)
        )[0], [1, 1, 1, 1]
    )

def test_everyone_trusted_some_penalized():
    np.testing.assert_array_equal(
        ao.computing_voting_rights_and_statistics(
            np.array([1, 1, 1, 1]), 
            np.array([0.5, 0.5, 1, 1])
        )[0], [0.5, 0.5, 1, 1]
    )

def test_untrusted_less_than_bias_get_full_voting_right():
    np.testing.assert_array_equal(
        ao.computing_voting_rights_and_statistics(
            np.array([0, 0.5, 0.5, 1, 1]), 
            np.ones(shape=5)
        )[0], [1, 1, 1, 1, 1]
    )

def test_untrusted_and_penalized_less_than_bias_get_penalized_voting_right():
    np.testing.assert_array_equal(
        ao.computing_voting_rights_and_statistics(
            np.array([0, 0.5, 0.5, 1, 1]), 
            np.array([0.7, 0.7, 0.7, 1, 1])
        )[0], [0.7, 0.7, 0.7, 1, 1]
    )
    
# The below test checks simple cases where trust scores are only 0 and 1
@pytest.mark.parametrize(
    "n_trusted, n_non_trusted",
    [
        (0, 2),
        (0, 100),
        (1, 1),
        (1, 50),
        (2, 3),
        (100, 50),
        (1000, 1000),
        (1000, 3),
    ],
)
def test_untrusted_get_partial_voting_right(n_trusted, n_non_trusted):
    expected_partial_right = min(
        (ao.min_overtrust + n_trusted * ao.overtrust_ratio) / n_non_trusted, 1
    )
    np.testing.assert_array_almost_equal(
        ao.computing_voting_rights_and_statistics(
            np.array([0] * n_non_trusted + [1] * n_trusted),
            np.ones(shape=n_non_trusted + n_trusted),
        )[0],
        [expected_partial_right] * n_non_trusted + [1] * n_trusted,
    )


@pytest.mark.parametrize(
    "n_random_users",
    [
        1,
        8,
        32,
        128,
        512,
        1024,
    ],
)
def test_random_input_voting_right_more_than_trust_score(n_random_users):
    trust_scores = np.random.random(size=(n_random_users,))
    voting_rights = ao.computing_voting_rights_and_statistics(trust_scores, np.ones(shape=n_random_users))[0]
    assert all(v >= t for v, t in zip(voting_rights, trust_scores))


@pytest.mark.parametrize(
    "n_random_users",
    [
        1,
        8,
        32,
        128,
        512,
        1024,
    ],
)
def test_total_over_trust_less_than_expected(n_random_users):
    trust_scores = np.random.random(size=(n_random_users,))
    voting_rights = ao.computing_voting_rights_and_statistics(trust_scores, np.ones(shape=n_random_users))[0]
    total_over_trust = (voting_rights - trust_scores).sum()
    expected_over_trust = ao.min_overtrust + trust_scores.sum() * ao.overtrust_ratio
    assert total_over_trust < expected_over_trust or np.isclose(
        total_over_trust, expected_over_trust
    )


@pytest.mark.parametrize(
    "n_random_users",
    [
        1,
        8,
        32,
        128,
        512,
        1024,
    ],
)
def test_total_over_trust_less_than_expected_with_random_penalizations(n_random_users):
    trust_scores = np.random.random(size=(n_random_users,))
    privacy_penalties = np.random.random(size=(n_random_users,))
    voting_rights = ao.computing_voting_rights_and_statistics(trust_scores, privacy_penalties)[0]
    total_over_trust = (voting_rights - trust_scores * privacy_penalties).sum()
    expected_over_trust = ao.min_overtrust + trust_scores.sum() * ao.overtrust_ratio
    assert total_over_trust < expected_over_trust or np.isclose(
        total_over_trust, expected_over_trust
    )


@pytest.mark.parametrize(
    "n_random_users",
    [
        1,
        8,
        32,
        128,
        512,
        1024,
    ],
)
def test_min_voting_right_more_than_min_trust(n_random_users):
    trust_scores = np.random.random(size=(n_random_users,))
    min_voting_right = ao.computing_voting_rights_and_statistics(
        trust_scores, np.ones(shape=n_random_users)
    )[0].min()
    min_trust_score = trust_scores.min()
    assert min_voting_right > min_trust_score


def test_voting_rights_abstraction():
    voting_rights = VotingRights()
    voting_rights[3, 46, "default"] = 0.4
    voting_rights[3, 46, "default"] *= 2
    assert voting_rights[3, 46, "default"] == 0.8


def test_affine_overtrust():
    users = Users(dict(username=list(range(5)), trust_score=[0.5, 0.6, 0.0, 0.4, 1]))
    entities = Entities(list(range(6)))
    made_public = MadePublic()
    made_public["0", "0"] = True
    made_public["0", "3"] = True
    made_public["1", "5"] = True
    made_public["2", "1"] = True
    made_public["4", "3"] = True
    
    assessments = Assessments()
    assessments["0", "default", "0"] = Assessment(2)
    assessments["3", "default", "0"] = Assessment(-1)
    assessments["3", "default", "1"] = Assessment(0)
    assessments["4", "default", "3"] = Assessment(5)
    
    comparisons = Comparisons()
    comparisons["0", "default", "3", "5"] = Comparison(-1)
    comparisons["1", "default", "1", "5"] = Comparison(1)
    comparisons["2", "default", "0", "1"] = Comparison(5)
    
    ao = AffineOvertrust(privacy_penalty=0.5, min_overtrust=2.0, overtrust_ratio=0.1)
    entities, voting_rights = ao(users, entities, made_public, assessments, comparisons)

    assert len(entities) == 6  # 6 entities
    assert list(entities.columns) == [
        'default_cumulative_trust', 
        'default_min_voting_right', 
        'default_overtrust'
    ]

    # Voting rights are assigned only on entities where evaluations have been made.
    assert voting_rights.keys("entity_name") == {"0", "1", "3", "5"}


@pytest.mark.parametrize("seed", range(5))
def test_affine_overtrust_test_data(seed):
    entities, voting_rights = ao.state2objects_function(states[seed])
    for (username, entity_name, criterion), voting_right in voting_rights:
        assert voting_right >= 0
