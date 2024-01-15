from solidago.generative_model.entity_model import SvdEntityModel
from solidago.generative_model.user_model import SvdUserModel
from solidago.generative_model.true_score_model import SvdTrueScoreModel
from solidago.generative_model.engagement_model import SimpleEngagementModel

def test_svd_user_model():
    users = SvdUserModel(svd_dimension=5)(n_users=50)
    entities = SvdEntityModel(svd_dimension=5)(n_entities=200)
    scores = SvdTrueScoreModel(noise_scale=0.5)(users, entities)
    comparisons = SimpleEngagementModel()(users, scores)
