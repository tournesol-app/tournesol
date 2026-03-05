import pytest
import numpy as np

from solidago import *


ao = poll_functions.AffineOvertrust(privacy_penalty=0.5, min_overtrust=2.0, overtrust_ratio=0.1, max_workers=1)

def test_empty_input():
    np.testing.assert_array_equal(
        ao.thread_function(
            np.array([]), 
            np.array([]),
            ao.overtrust_ratio,
            ao.min_overtrust,
        )[0], []
    )

def test_everyone_trusted():
    np.testing.assert_array_equal(
        ao.thread_function(
            np.array([1, 1, 1, 1]), 
            np.ones(shape=4),
            ao.overtrust_ratio,
            ao.min_overtrust,
        )[0], [1, 1, 1, 1]
    )

def test_everyone_trusted_some_penalized():
    np.testing.assert_array_equal(
        ao.thread_function(
            np.array([1, 1, 1, 1]), 
            np.array([0.5, 0.5, 1, 1]),
            ao.overtrust_ratio,
            ao.min_overtrust,
        )[0], [0.5, 0.5, 1, 1]
    )

def test_untrusted_less_than_bias_get_full_voting_right():
    np.testing.assert_array_equal(
        ao.thread_function(
            np.array([0, 0.5, 0.5, 1, 1]), 
            np.ones(shape=5),
            ao.overtrust_ratio,
            ao.min_overtrust,
        )[0], [1, 1, 1, 1, 1]
    )

def test_untrusted_and_penalized_less_than_bias_get_penalized_voting_right():
    np.testing.assert_array_equal(
        ao.thread_function(
            np.array([0, 0.5, 0.5, 1, 1]), 
            np.array([0.7, 0.7, 0.7, 1, 1]),
            ao.overtrust_ratio,
            ao.min_overtrust,
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
        ao.thread_function(
            np.array([0] * n_non_trusted + [1] * n_trusted),
            np.ones(shape=n_non_trusted + n_trusted),
            ao.overtrust_ratio,
            ao.min_overtrust,
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
    voting_rights = ao.thread_function(
        trust_scores, 
        np.ones(shape=n_random_users),
        ao.overtrust_ratio,
        ao.min_overtrust,
    )[0]
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
    voting_rights = ao.thread_function(
        trust_scores, 
        np.ones(shape=n_random_users),
        ao.overtrust_ratio,
        ao.min_overtrust,
    )[0]
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
    voting_rights = ao.thread_function(
        trust_scores, 
        privacy_penalties,
        ao.overtrust_ratio,
        ao.min_overtrust,
    )[0]
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
    min_voting_right = ao.thread_function(
        trust_scores, 
        np.ones(shape=n_random_users),
        ao.overtrust_ratio,
        ao.min_overtrust,
    )[0].min()
    min_trust_score = trust_scores.min()
    assert min_voting_right > min_trust_score

def test_voting_rights_abstraction():
    voting_rights = VotingRights()
    voting_rights.set(username="3", entity_name="46", criterion="default", voting_right=0.4)
    voting_right = voting_rights.get(username="3", entity_name="46", criterion="default")["voting_right"]
    voting_rights.set(username="3", entity_name="46", criterion="default", voting_right=2*voting_right)
    assert voting_rights.get(username="3", entity_name="46", criterion="default")["voting_right"] == 0.8

def test_affine_overtrust():
    users = Users([str(i) for i in range(5)])
    users = users.assign(trust=[0.5, 0.6, 0.0, 0.4, 1])
    entities = Entities([str(i) for i in range(6)])
    public_settings = PublicSettings()
    public_settings.set(username="0", entity_name="0", public=True)
    public_settings.set(username="0", entity_name="3", public=True)
    public_settings.set(username="1", entity_name="5", public=True)
    public_settings.set(username="2", entity_name="1", public=True)
    public_settings.set(username="4", entity_name="3", public=True)
    
    ratings = Ratings()
    ratings.set(username="0", criterion="default", entity_name="0", value=2)
    ratings.set(username="3", criterion="default", entity_name="0", value=-1)
    ratings.set(username="3", criterion="default", entity_name="1", value=0)
    ratings.set(username="4", criterion="default", entity_name="3", value=5)
    
    comparisons = Comparisons()
    comparisons.set(username="0", criterion="default", left_name="3", right_name="5", value=-1)
    comparisons.set(username="1", criterion="default", left_name="1", right_name="5", value=1)
    comparisons.set(username="2", criterion="default", left_name="0", right_name="1", value=5)
    
    ao = poll_functions.AffineOvertrust(privacy_penalty=0.5, min_overtrust=2.0, overtrust_ratio=0.1, max_workers=1)
    result_entities, voting_rights = ao.fn(users, entities, public_settings, ratings, comparisons)

    assert isinstance(result_entities, Entities)
    assert isinstance(voting_rights, VotingRights)

    assert len(result_entities) == 6  # 6 entities
    assert list(result_entities.df.columns) == [
        'default_cumulative_trust', 
        'default_min_voting_right', 
        'default_overtrust'
    ]

    # Voting rights are assigned only on entities where evaluations have been made.
    assert voting_rights.keys("entity_name") == {"0", "1", "3", "5"}
