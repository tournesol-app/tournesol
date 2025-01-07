import pytest
from solidago import *


def test_users():
    users = Users([
        ["aidjango", 12521],
        ["le_science4all", 1325],
    ], columns=["username", "n_comparisons"])
    assert len(users) == 2
    assert users.get("aidjango")["n_comparisons"] == 12521
    assert len(users.get({"aidjango", "le_science4all"})) == 2

def test_vector_users():
    users = VectorUsers(np.array([
        [0, 1, 2],
        [3, 4, 5],
    ]), [
        ["aidjango", 12521],
        ["le_science4all", 1325],
    ], columns=["username", "n_comparisons"])
    assert len(users) == 2
    assert users.get("aidjango")["n_comparisons"] == 12521
    assert len(users.get({"aidjango", "le_science4all"})) == 2
