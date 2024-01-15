from solidago.generative_model.user_model import SvdUserModel
from solidago.generative_model.vouch_model import ErdosRenyiVouchModel

def test_erdos_renyi_vouch():
    users = SvdUserModel(p_trustworthy=0.8, p_pretrusted=0.2, svd_dimension=5)(50)
    vouches = ErdosRenyiVouchModel()(users)
    for _, row in vouches.iterrows():
        trusted_voucher = users.loc[row["voucher"], "is_trustworthy"]
        trusted_vouchee = users.loc[row["vouchee"], "is_trustworthy"]
        assert trusted_voucher == trusted_vouchee
    
