import numpy as np
from solidago.poll.poll_tables import User, Users


def test_user():
    user = User("lpfaucon", vector=[1., 2.], trust=0.5)
    assert all(user.vector == np.array([1., 2.]))
    assert user["trust"] == 0.5
    assert user["pretrust"] == False


def test_users():
    users = Users([
        ["aidjango", 12521, 0, 1, 2],
        ["le_science4all", 3163, 3., 4, 5],
    ], columns=["name", "n_comparisons", "v0", "v1", "v2"])
    assert len(users) == 2
    assert users["aidjango"]["n_comparisons"] == 12521
    assert len(users[["aidjango", "le_science4all"]]) == 2 # type: ignore
