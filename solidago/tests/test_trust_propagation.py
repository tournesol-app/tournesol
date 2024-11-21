import pytest
import importlib
import pandas as pd

from solidago.pipeline.inputs import TournesolDataset
from solidago.trust_propagation.lipschitrust import LipschiTrust
from solidago.trust_propagation.trust_all import TrustAll

from solidago.generative_model.user_model import NormalUserModel
from solidago.generative_model.vouch_model import ErdosRenyiVouchModel


def test_lipschitrust_simple():
    users = pd.DataFrame({"is_pretrusted": [True, True, False, False, False]})
    users.index.name = "user_id"
    vouches = pd.DataFrame(
        {
            "voucher": [0, 0, 2, 3],
            "vouchee": [1, 2, 3, 4],
            "vouch": 1.0,
        }
    )
    trust_propagator = LipschiTrust(pretrust_value=0.8, decay=0.8, sink_vouch=5.0, error=1e-8)
    users = trust_propagator(users, vouches)
    assert users.loc[0, "trust_score"] == 0.8
    assert users.loc[4, "trust_score"] > 0
    assert users.loc[2, "trust_score"] == pytest.approx(0.8 * 0.8 / 7), users


def test_lipschitrust_generative():
    users = NormalUserModel(p_trustworthy=0.8, p_pretrusted=0.2, svd_dimension=5)(50)
    vouches = ErdosRenyiVouchModel()(users)

    trust_propagator = LipschiTrust(pretrust_value=0.8, decay=0.8, sink_vouch=5.0, error=1e-8)

    users = trust_propagator(users, vouches)
    for _, row in users.iterrows():
        assert row["is_trustworthy"] or (row["trust_score"] == 0)


def test_lipschitrust_ten_users():
    users = pd.DataFrame(
        {"is_pretrusted": [False, True, False, True, False, False, True, False, False, False]}
    )
    users.index.name = "user_id"
    vouches = pd.DataFrame(
        [
            [1, 0],
            [1, 3],
            [1, 7],
            [2, 5],
            [3, 1],
            [3, 5],
            [4, 7],
            [5, 1],
            [7, 1],
            [7, 2],
            [8, 3],
            [9, 4],
            [9, 5],
        ],
        columns=["voucher", "vouchee"],
    )
    vouches["vouch"] = 1.0
    trust_propagator = LipschiTrust(pretrust_value=0.8, decay=0.8, sink_vouch=5.0, error=1e-8)

    users = trust_propagator(users, vouches)
    assert users.loc[1, "trust_score"] > 0.8
    assert users.loc[2, "trust_score"] > 0.0
    assert users.loc[8, "trust_score"] == 0.0
    assert users.loc[9, "trust_score"] == 0.0

    # Add one vouch: 1 -> 8
    vouches = pd.concat([vouches, pd.DataFrame([{"voucher": 1, "vouchee": 8, "vouch": 1}])])
    users = trust_propagator(users, vouches)
    assert users.loc[8, "trust_score"] > 0.0


@pytest.mark.parametrize("test", range(4))
def test_lipschitrust_test_data(test):
    td = importlib.import_module(f"data.data_{test}")
    trusts = td.pipeline.trust_propagation(td.users, td.vouches)
    for user, row in td.users.iterrows():
        assert trusts.loc[user, "trust_score"] == pytest.approx(row["trust_score"])


def test_trust_all():
    users = pd.DataFrame({"is_pretrusted": [True, True, False, False, False]})
    vouches = pd.DataFrame(
        {"voucher": [0, 0, 2, 3], "vouchee": [1, 2, 3, 4], "vouch": [1, 1, 1, 1]}
    )
    users = TrustAll()(users, vouches)
    assert users.loc[0, "trust_score"] == 1.0
    assert users.loc[4, "trust_score"] == 1.0
    assert users.loc[2, "trust_score"] == 1.0
