import numpy as np
import pytest

from vouch.voting_rights import OVER_TRUST_BIAS, OVER_TRUST_SCALE, compute_voting_rights


def test_empty_input():
    np.testing.assert_array_equal(compute_voting_rights([]), [])


def test_everyone_trusted():
    np.testing.assert_array_equal(compute_voting_rights([1, 1, 1, 1]), [1, 1, 1, 1])


def test_untrusted_less_than_bias_get_full_voting_right():
    np.testing.assert_array_equal(
        compute_voting_rights([0, 0.5, 0.5, 1, 1]), [1, 1, 1, 1, 1]
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
    np.testing.assert_array_equal(
        compute_voting_rights([0] * n_non_trusted + [1] * n_trusted),
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
    voting_rights = compute_voting_rights(trust_scores)
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
    voting_rights = compute_voting_rights(trust_scores)
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
def test_min_voting_right_more_than_min_trust(n_random_users):
    trust_scores = np.random.random(size=(n_random_users,))
    min_voting_right = compute_voting_rights(trust_scores).min()
    min_trust_score = trust_scores.min()
    assert min_voting_right > min_trust_score
