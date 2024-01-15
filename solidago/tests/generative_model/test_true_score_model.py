from solidago.generative_model.entity_model import SvdEntityModel
from solidago.generative_model.user_model import SvdUserModel
from solidago.generative_model.true_score_model import SvdTrueScoreModel

def test_svd_user_model():
    users = SvdUserModel(svd_dimension=5)(n_users=50)
    entities = SvdEntityModel(svd_dimension=5)(n_entities=100)
    scores = SvdTrueScoreModel(noise_scale=0.5)(users, entities)
    assert len(scores) == len(users)
    assert len(scores.columns) == len(entities)
    
