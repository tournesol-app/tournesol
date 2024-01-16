import pytest
import pandas as pd

from solidago.pipeline.inputs import TournesolInputFromPublicDataset
from solidago.trust_propagation.lipschitrust import LipschiTrust
from solidago.generative_model.user_model import SvdUserModel
from solidago.generative_model.vouch_model import ErdosRenyiVouchModel

def test_lipschitrust_simple():
    users = pd.DataFrame({ 
        "is_pretrusted": [True, True, False, False, False]
    })
    vouches = pd.DataFrame({
        "voucher": [0, 0, 2, 3],
        "vouchee": [1, 2, 3, 4],
        "vouch": [1, 1, 1, 1]
    })
    trust_propagator = LipschiTrust(
        pretrust_value=0.8,
        decay=0.8,
        sink_vouch=5.0,
        error=1e-8
    )
    trusts = trust_propagator(users, vouches)
    assert trusts[0] == 0.8
    assert trusts[4] > 0
    assert trusts[2] == pytest.approx(0.8 * 0.8 / 7)

def test_lipschitrust_generative():
    users = SvdUserModel(p_trustworthy=0.8, p_pretrusted=0.2, svd_dimension=5)(50)
    vouches = ErdosRenyiVouchModel()(users)
    
    trust_propagator = LipschiTrust(
        pretrust_value=0.8,
        decay=0.8,
        sink_vouch=5.0,
        error=1e-8
    )
    
    trusts = trust_propagator(users, vouches)
    for user, row in users.iterrows():
        assert row["is_trustworthy"] or (user not in trusts) or trusts[user] == 0.0
