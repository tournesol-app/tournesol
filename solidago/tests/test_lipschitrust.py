import pytest
import pandas as pd

from solidago.trust_propagation.lipschitrust import LipschiTrust

def test_compute_trusts():
    users = pd.DataFrame({ 
        "public_username": ["le_science4all", "aidjango", "amatissart",
            "lpfaucon", "biscuissec"],
        "is_pretrusted": [True, True, False, False, False]
    }).set_index("public_username")
    vouches = pd.DataFrame({
        "voucher": ["le_science4all", "le_science4all", "lpfaucon",
            "biscuissec"],
        "vouchee": ["amatissart", "lpfaucon", "biscuissec", "aidjango"],
        "vouch": [1, 1, 1, 1]
    })
    trust_propagator = LipschiTrust(
        pretrust_value=0.8,
        decay=0.8,
        sink_vouch=5.0,
        error=1e-8
    )
    trusts = trust_propagator.compute_trusts(users, vouches)
    assert trusts["le_science4all"] == 0.8
    assert trusts["aidjango"] > 0
    assert trusts["amatissart"] == pytest.approx(0.8 * 0.8 / 7)

def test_data():
    users = pd.read_csv("tests/data/users.csv", index_col="public_username")
    vouches = pd.read_csv("tests/data/vouches.csv")
    trust_propagator = LipschiTrust(
        pretrust_value=0.8,
        decay=0.8,
        sink_vouch=5.0,
        error=1e-8
    )
    trusts = trust_propagator.compute_trusts(users, vouches)
    usernames = ["le_science4all", "aidjango", "Þþanon"]
    for u in usernames:
      assert trusts[u] == pytest.approx(users.loc[u]["trust_score"])
    
