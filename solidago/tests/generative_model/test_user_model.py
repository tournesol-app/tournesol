from solidago.generative_model.user_model import SvdUserModel

def test_svd_user_model():
    user_model = SvdUserModel(svd_dimension=5)
    users = user_model(n_users=10)
    assert len(users) == 10
    for u in range(len(users)):
        assert users.loc[u, "is_trustworthy"] or not users.loc[u, "is_pretrusted"]

