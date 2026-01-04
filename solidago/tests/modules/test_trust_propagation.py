import pytest

from solidago import *
from solidago.functions.trust_propagation import LipschiTrust, TrustAll
N_SEEDS = 3

polls = [ Poll.load(f"tests/saved/{seed}") for seed in range(N_SEEDS) ]


def test_lipschitrust_simple():
    users0 = Users(range(5))
    users0 = users0.assign(is_pretrusted=[True, True, False, False, False])
    vouches = Vouches(init_data={
        (0, 1, "Personhood"): (1, 0),
        (0, 2, "Personhood"): (1, 0),
        (2, 3, "Personhood"): (1, 0),
        (3, 4, "Personhood"): (1, 0)
    })
    users = LipschiTrust(pretrust_value=0.8, decay=0.8, sink_vouch=5.0, error=1e-8)(users0, vouches)
    assert users[0].trust == 0.8
    assert users[4].trust > 0
    assert users[2].trust == pytest.approx(0.8 * 0.8 / 2), users


@pytest.mark.parametrize("seed", range(N_SEEDS))
def test_lipschitrust_generative(seed):
    trust_propagator = LipschiTrust(pretrust_value=0.8, decay=0.8, sink_vouch=5.0, error=1e-8,)

    users = trust_propagator(polls[seed].users, polls[seed].vouches)
    for user in users:
        assert user.is_trustworthy or (user.trust == 0)


def test_lipschitrust_ten_users():
    users = Users([str(i) for i in range(10)])
    users = users.assign(is_pretrusted=[False, True, False, True, False, False, True, False, False, False])
    vouches = Vouches(init_data={
        ("1", "0", "Personhood"): (1, 0),
        ("1", "3", "Personhood"): (1, 0),
        ("1", "7", "Personhood"): (1, 0),
        ("2", "5", "Personhood"): (1, 0),
        ("3", "1", "Personhood"): (1, 0),
        ("3", "5", "Personhood"): (1, 0),
        ("4", "7", "Personhood"): (1, 0),
        ("5", "1", "Personhood"): (1, 0),
        ("7", "1", "Personhood"): (1, 0),
        ("7", "2", "Personhood"): (1, 0),
        ("8", "3", "Personhood"): (1, 0),
        ("9", "4", "Personhood"): (1, 0),
        ("9", "5", "Personhood"): (1, 0),
    })
    
    trust_propagator = LipschiTrust(pretrust_value=0.8, decay=0.8, sink_vouch=5.0, error=1e-8)
    users = trust_propagator(users, vouches)
    assert users["1"]["trust"] > 0.8
    assert users["2"]["trust"] > 0.0
    assert users["8"]["trust"] == 0.0
    assert users["9"]["trust"] == 0.0

    # Add one vouch: 1 -> 8
    vouches["1", "8", "Personhood"] = (1, 0)
    users = trust_propagator(users, vouches)
    assert users["8"].trust > 0.0


@pytest.mark.parametrize("seed", range(N_SEEDS))
def test_lipschitrust_test_data(seed):
    pipeline = load("tests/modules/test_pipeline.yaml")
    assert isinstance(pipeline, Sequential)
    users = pipeline.modules[0](polls[seed].users, polls[seed].vouches)
    for user in users:
        assert user["is_trustworthy"] or (user.trust == 0)


def test_trust_all():
    users = Users(range(5))
    users = users.assign(is_pretrusted=[True, True, False, False, False])
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
        assert user.trust == 1.0
        
