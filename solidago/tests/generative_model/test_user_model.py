from solidago.generative_model.user_model import SvdUserModel

def test_user_model():
    user_model = SvdUserModel(svd_dimension=5)
    users = user_model(n_users=10)
    assert len(users) == 10
