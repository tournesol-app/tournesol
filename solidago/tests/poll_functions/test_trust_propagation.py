import pytest

from solidago import *
from solidago.poll_functions.trust_propagation import LipschiTrust, TrustAll


def test_lipschitrust_main():
    import numpy as np
    bys = np.array([0, 0, 2, 3], dtype=np.int64)
    tos = np.array([1, 2, 3, 4], dtype=np.int64)
    weights = np.array([1, 1, 1, 1], dtype=np.float64)
    pretrusts = np.array([.8, .8, 0, 0, .8], dtype=np.float64)
    sink_vouch = 5.
    decay = .7
    error = 1e-8

    trusts = LipschiTrust.main(bys, tos, weights, pretrusts, sink_vouch, decay, error)
    assert trusts[0] == 0.8
    assert trusts[4] > 0
    assert trusts[2] == pytest.approx(0.8 * 0.7 / (5 + 2)), trusts


def test_lipschitrust_simple():
    users0 = Users(dict(name=["0", "1", "2", "3", "4"]))
    users0 = users0.assign(pretrust=[True, True, False, False, False])
    socials = Socials([
        ("0", "1", "Personhood", 1, 0),
        ("0", "2", "Personhood", 1, 0),
        ("2", "3", "Personhood", 1, 0),
        ("3", "4", "Personhood", 1, 0),
    ], columns=["by", "to", "kind", "weight", "priority"])
    users = LipschiTrust(pretrust_value=0.8, decay=0.8, sink_vouch=5.0, error=1e-8).fn(users0, socials)
    assert users[0]["trust"] == 0.8
    assert users[4]["trust"] > 0 # type: ignore
    assert users[2]["trust"] == pytest.approx(0.8 * 0.8 / (5 + 2)), users


def test_lipschitrust_ten_users():
    users = Users(dict(name=[str(i) for i in range(10)]))
    users = users.assign(pretrust=[False, True, False, True, False, False, True, False, False, False])
    socials = Socials([
        ("1", "0", "Personhood", 1, 0),
        ("1", "3", "Personhood", 1, 0),
        ("1", "7", "Personhood", 1, 0),
        ("2", "5", "Personhood", 1, 0),
        ("3", "1", "Personhood", 1, 0),
        ("3", "5", "Personhood", 1, 0),
        ("4", "7", "Personhood", 1, 0),
        ("5", "1", "Personhood", 1, 0),
        ("7", "1", "Personhood", 1, 0),
        ("7", "2", "Personhood", 1, 0),
        ("8", "3", "Personhood", 1, 0),
        ("9", "4", "Personhood", 1, 0),
        ("9", "5", "Personhood", 1, 0),
    ], columns=["by", "to", "kind", "weight", "priority"])
    
    trust_propagator = LipschiTrust(pretrust_value=0.8, decay=0.8, sink_vouch=5.0, error=1e-8)
    users = trust_propagator.fn(users, socials)
    assert users["1"]["trust"] > 0.8 # type: ignore
    assert users["2"]["trust"] > 0.0 # type: ignore
    assert users["8"]["trust"] == 0.0
    assert users["9"]["trust"] == 0.0

    # Add one vouch: 1 -> 8
    socials.set(by="1", to="8", kind="Personhood", weight=1, priority=0)
    users = trust_propagator.fn(users, socials)
    assert users["8"]["trust"] > 0.0 # type: ignore


def test_trust_all():
    users = Users(range(5))
    users = users.assign(pretrust=[True, True, False, False, False])
    out_users = TrustAll().fn(users)
    for user in out_users:
        assert user["trust"] == 1.0
        
