from solidago.generative_model.user_model import NormalUserModel
from solidago.generative_model.vouch_model import ErdosRenyiVouchModel
from solidago.generative_model.entity_model import NormalEntityModel
from solidago.generative_model.engagement_model import SimpleEngagementModel
from solidago.generative_model.comparison_model import KnaryGBT
from solidago.generative_model import GenerativeModel

def test_svd_user_model():
    user_model = NormalUserModel(svd_dimension=5)
    users = user_model(n_users=10)
    assert len(users) == 10
    for u in range(len(users)):
        assert users.loc[u, "is_trustworthy"] or not users.loc[u, "is_pretrusted"]

def test_erdos_renyi_vouch():
    users = NormalUserModel(p_trustworthy=0.8, p_pretrusted=0.2, svd_dimension=5)(50)
    vouches = ErdosRenyiVouchModel()(users)
    for _, row in vouches.iterrows():
        trusted_voucher = users.loc[row["voucher"], "is_trustworthy"]
        trusted_vouchee = users.loc[row["vouchee"], "is_trustworthy"]
        assert trusted_voucher == trusted_vouchee
    
def test_svd_entity_model():
    entity_model = NormalEntityModel(svd_dimension=5)
    entities = entity_model(n_entities=100)
    assert len(entities) == 100

def test_engagement_model():
    users = NormalUserModel(svd_dimension=5)(n_users=20)
    entities = NormalEntityModel(svd_dimension=5)(n_entities=50)
    _, judgments = SimpleEngagementModel()(users, entities)
    
def test_comparison_model():
    users = NormalUserModel(svd_dimension=5)(n_users=20)
    entities = NormalEntityModel(svd_dimension=5)(n_entities=50)
    privacy, judgments = SimpleEngagementModel()(users, entities)
    judgments.comparisons = KnaryGBT(21, 10)(users, entities, judgments.comparisons)

def test_generative_model():
    users, vouches, entities, privacy, judgments = GenerativeModel()(20, 50)
    assert len(users) == 20

