import pytest
import pandas as pd

from solidago.collaborative_scaling import estimate_positive_score_shift

def test_score_shift_when_all_scores_are_equal():
    scaled_individual_scores = pd.DataFrame(dict(
        user_id=[f"user_{i}" for i in range(1000)],
        entity_id=[f"entity_{i}" for i in range(1000)],
        score=12.12,
        uncertainty=1e-12,
    ))
    tau = estimate_positive_score_shift(
        scaled_individual_scores,
        W=1,
        quantile=0.05
    )
    assert tau == pytest.approx(12.12)

def test_all_users_equal_voting_right_for_score_shift():
    scaled_individual_scores = pd.DataFrame(dict(
        user_id=["louis"] * 998 + ["adrien", "aidan"],
        entity_id=["entity_{i}" for i in range(1000)],
        score=[-10] * 998 + [10, 10],
        uncertainty=1e-12,
    ))
    tau = estimate_positive_score_shift(
        scaled_individual_scores,
        W=1,
        quantile=1/3
    )
    assert tau == pytest.approx(0, abs=1e-4)



def test_5_percent_percentile_score_shift_has_expected_value():
    scaled_individual_scores = pd.DataFrame(dict(
        user_id=["user_{i}" for i in range(1000)],
        entity_id=["entity_{i}" for i in range(1000)],
        score=[i for i in range(1, 1001)],
        uncertainty=1e-12,
    ))
    tau = estimate_positive_score_shift(
        scaled_individual_scores,
        W=1e-12,
        quantile=0.05
    )
    assert tau == pytest.approx(50, abs=1e-4)



def test_large_W_pulls_score_shift_towards_zero():
    scaled_individual_scores = pd.DataFrame(dict(
        user_id=["user_{i}" for i in range(1000)],
        entity_id=["entity_{i}" for i in range(1000)],
        score=[i for i in range(1, 1001)],
        uncertainty=1e-12,
    ))
    tau = estimate_positive_score_shift(
        scaled_individual_scores,
        W=100,
        quantile=0.05
    )
    assert tau < 50
