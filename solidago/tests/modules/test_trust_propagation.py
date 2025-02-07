import pytest
import importlib
import pandas as pd

from solidago import *
from solidago.modules.trust_propagation import LipschiTrust, TrustAll

states = [ State.load(f"tests/modules/saved/{seed}") for seed in range(5) ]


def test_lipschitrust_simple():
    users = Users({"username": list(range(5)), "is_pretrusted": [True, True, False, False, False]})
    vouches = Vouches(data=[
        ["0", "1", "Personhood", 1, 0],
        ["0", "2", "Personhood", 1, 0],
        ["2", "3", "Personhood", 1, 0],
        ["3", "4", "Personhood", 1, 0]
    ])
    users = LipschiTrust(pretrust_value=0.8, decay=0.8, sink_vouch=5.0, error=1e-8)(users, vouches)
    assert users.get("0")["trust_score"] == 0.8
    assert users.get("4")["trust_score"] > 0
    assert users.get("2")["trust_score"] == pytest.approx(0.8 * 0.8 / 2), users


@pytest.mark.parametrize("seed", range(4))
def test_lipschitrust_generative(seed):
    trust_propagator = LipschiTrust(pretrust_value=0.8, decay=0.8, sink_vouch=5.0, error=1e-8)

    users = trust_propagator(states[seed].users, states[seed].vouches)
    for user in users:
        assert user["is_trustworthy"] or (user["trust_score"] == 0)


def test_lipschitrust_ten_users():
    users = Users({
        "username": list(range(10)),
        "is_pretrusted": [False, True, False, True, False, False, True, False, False, False]
    })
    vouches = Vouches(data=[
        ["1", "0", "Personhood", 1, 0],
        ["1", "3", "Personhood", 1, 0],
        ["1", "7", "Personhood", 1, 0],
        ["2", "5", "Personhood", 1, 0],
        ["3", "1", "Personhood", 1, 0],
        ["3", "5", "Personhood", 1, 0],
        ["4", "7", "Personhood", 1, 0],
        ["5", "1", "Personhood", 1, 0],
        ["7", "1", "Personhood", 1, 0],
        ["7", "2", "Personhood", 1, 0],
        ["8", "3", "Personhood", 1, 0],
        ["9", "4", "Personhood", 1, 0],
        ["9", "5", "Personhood", 1, 0],
    ])
    
    trust_propagator = LipschiTrust(pretrust_value=0.8, decay=0.8, sink_vouch=5.0, error=1e-8)
    users = trust_propagator(users, vouches)
    assert users.get("1")["trust_score"] > 0.8
    assert users.get("2")["trust_score"] > 0.0
    assert users.get("8")["trust_score"] == 0.0
    assert users.get("9")["trust_score"] == 0.0

    # Add one vouch: 1 -> 8
    vouches.set("1", "8", "Personhood", 1, 0)
    users = trust_propagator(users, vouches)
    assert users.get("8")["trust_score"] > 0.0


@pytest.mark.parametrize("seed", range(4))
def test_lipschitrust_test_data(seed):
    pipeline = Sequential.load("tests/modules/test_pipeline.json")
    users = pipeline.trust_propagation(states[seed].users, states[seed].vouches)
    for user in users:
        assert user["is_trustworthy"] or (user["trust_score"] == 0)


def test_trust_all():
    users = Users({"username": list(range(5)), "is_pretrusted": [True, True, False, False, False]})
    vouches = Vouches({
        "0": {
            "1": { "Personhood": (1, 0) },
            "2": { "Personhood": (1, 0) },
        },
        "2": {
            "3": { "Personhood": (1, 0) },
        },
        "3": {
            "4": { "Personhood": (1, 0) },
        },
    })
    out_users = TrustAll()(users, vouches)
    for user in out_users:
        assert user["trust_score"] == 1.0
        
