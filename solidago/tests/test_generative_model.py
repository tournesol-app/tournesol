from solidago.generative_model.user_model import SvdUserModel
from solidago.generative_model.vouch_model import ErdosRenyiVouchModel
from solidago.generative_model.entity_model import SvdEntityModel
from solidago.generative_model.true_score_model import SvdTrueScoreModel
from solidago.generative_model.engagement_model import SimpleEngagementModel
from solidago.generative_model.comparison_model import KnaryGBT
from solidago.generative_model import GenerativeModel

def test_svd_user_model():
    user_model = SvdUserModel(svd_dimension=5)
    users = user_model(n_users=10)
    assert len(users) == 10
    for u in range(len(users)):
        assert users.loc[u, "is_trustworthy"] or not users.loc[u, "is_pretrusted"]

def test_erdos_renyi_vouch():
    users = SvdUserModel(p_trustworthy=0.8, p_pretrusted=0.2, svd_dimension=5)(50)
    vouches = ErdosRenyiVouchModel()(users)
    for _, row in vouches.iterrows():
        trusted_voucher = users.loc[row["voucher"], "is_trustworthy"]
        trusted_vouchee = users.loc[row["vouchee"], "is_trustworthy"]
        assert trusted_voucher == trusted_vouchee
    
def test_true_score_model():
    users = SvdUserModel(svd_dimension=5)(n_users=50)
    entities = SvdEntityModel(svd_dimension=5)(n_entities=100)
    scores = SvdTrueScoreModel(noise_scale=0.5)(users, entities)
    assert len(scores) == len(users)
    assert len(scores.columns) == len(entities)
    
def test_svd_entity_model():
    entity_model = SvdEntityModel(svd_dimension=5)
    entities = entity_model(n_entities=100)
    assert len(entities) == 100

def test_engagement_model():
    users = SvdUserModel(svd_dimension=5)(n_users=50)
    entities = SvdEntityModel(svd_dimension=5)(n_entities=200)
    scores = SvdTrueScoreModel(noise_scale=0.5)(users, entities)
    assessments, comparisons = SimpleEngagementModel()(users, scores)
    
def test_comparison_model():
    users = SvdUserModel(svd_dimension=5)(n_users=50)
    entities = SvdEntityModel(svd_dimension=5)(n_entities=200)
    scores = SvdTrueScoreModel(noise_scale=0.5)(users, entities)
    assessments, comparisons = SimpleEngagementModel()(users, scores)
    comparisons = KnaryGBT(21, 10)(scores, comparisons)

def test_generative_model():
    data = GenerativeModel()(50, 200)
    assert len(data.users) == 50
