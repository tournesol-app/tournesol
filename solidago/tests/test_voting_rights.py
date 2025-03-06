import pytest
import importlib
import numpy as np
import pandas as pd

from functools import partial

from solidago.voting_rights.compute_voting_rights import compute_voting_rights

from solidago.privacy_settings import PrivacySettings
from solidago.voting_rights import VotingRights
from solidago.voting_rights.affine_overtrust import AffineOvertrust


# Params that will be used for tests
OVER_TRUST_BIAS = 2
OVER_TRUST_SCALE = 0.1

compute_voting_rights_with_params = partial(
    compute_voting_rights,
    over_trust_bias=OVER_TRUST_BIAS,
    over_trust_scale=OVER_TRUST_SCALE,
)


def test_empty_input():
    np.testing.assert_array_equal(
        compute_voting_rights_with_params(np.array([]), np.array([])), []
    )


def test_everyone_trusted():
    trust_scores, privacy_penalties = np.array([1, 1, 1, 1]), np.ones(shape=4)
    np.testing.assert_array_equal(
        compute_voting_rights_with_params(trust_scores, privacy_penalties), [1, 1, 1, 1]
    )


def test_everyone_trusted_some_penalized():
    trust_scores, privacy_penalties = np.array([1, 1, 1, 1]), np.array([0.5, 0.5, 1, 1])
    np.testing.assert_array_equal(
        compute_voting_rights_with_params(trust_scores, privacy_penalties), [0.5, 0.5, 1, 1]
    )


def test_untrusted_less_than_bias_get_full_voting_right():
    np.testing.assert_array_equal(
        compute_voting_rights_with_params(np.array([0, 0.5, 0.5, 1, 1]), np.ones(shape=5)),
        [1, 1, 1, 1, 1],
    )


def test_untrusted_and_penalized_less_than_bias_get_penalized_voting_right():
    np.testing.assert_array_equal(
        compute_voting_rights_with_params(
            np.array([0, 0.5, 0.5, 1, 1]), np.array([0.7, 0.7, 0.7, 1, 1])
        ),
        [0.7, 0.7, 0.7, 1, 1],
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
        (OVER_TRUST_BIAS + n_trusted * OVER_TRUST_SCALE) / n_non_trusted, 1
    )
    np.testing.assert_array_almost_equal(
        compute_voting_rights_with_params(
            np.array([0] * n_non_trusted + [1] * n_trusted),
            np.ones(shape=n_non_trusted + n_trusted),
        ),
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
    voting_rights = compute_voting_rights_with_params(trust_scores, np.ones(shape=n_random_users))
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
    voting_rights = compute_voting_rights_with_params(trust_scores, np.ones(shape=n_random_users))
    total_over_trust = (voting_rights - trust_scores).sum()
    expected_over_trust = OVER_TRUST_BIAS + trust_scores.sum() * OVER_TRUST_SCALE
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
    voting_rights = compute_voting_rights_with_params(trust_scores, privacy_penalties)
    total_over_trust = (voting_rights - trust_scores * privacy_penalties).sum()
    expected_over_trust = OVER_TRUST_BIAS + trust_scores.sum() * OVER_TRUST_SCALE
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
    min_voting_right = compute_voting_rights_with_params(
        trust_scores, np.ones(shape=n_random_users)
    ).min()
    min_trust_score = trust_scores.min()
    assert min_voting_right > min_trust_score


def test_voting_rights_abstraction():
    voting_rights = VotingRights()
    voting_rights[3, 46] = 0.4
    voting_rights[3, 46] *= 2
    assert voting_rights[3, 46] == 0.8


def test_affine_overtrust():
    users = pd.DataFrame(dict(trust_score=[0.5, 0.6, 0.0, 0.4, 1]))
    users.index.name = "user_id"
    vouches = pd.DataFrame()
    entities = pd.DataFrame(dict(entity_id=range(6)))
    entities.set_index("entity_id")
    privacy = PrivacySettings(
        {
            0: {0: True, 2: False, 3: False},
            1: {1: False, 2: True, 3: False},
            3: {0: True, 4: True},
            5: {0: False, 1: True},
        }
    )
    voting_rights_assignment = AffineOvertrust(
        privacy_penalty=0.5, min_overtrust=2.0, overtrust_ratio=0.1
    )
    voting_rights, entities = voting_rights_assignment(
        users, entities, vouches, privacy, user_models=None
    )

    assert len(entities) == 6  # 6 entities
    assert list(entities.columns) == [
        "entity_id",
        "cumulative_trust",
        "min_voting_right",
        "overtrust",
    ]

    # Voting rights are assigned only on entities where privacy settings are defined.
    assert voting_rights.entities() == {0, 1, 3, 5}


@pytest.mark.parametrize("test", range(4))
def test_affine_overtrust_test_data(test):
    td = importlib.import_module(f"data.data_{test}")
    voting_rights, entities = td.pipeline.voting_rights(
        td.users, td.entities, td.vouches, td.privacy, user_models=None,
    )
    for entity in td.voting_rights.entities():
        for user in td.voting_rights.on_entity(entity):
            assert td.voting_rights[user, entity] == voting_rights[user, entity]
