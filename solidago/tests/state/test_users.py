import pytest
import numpy as np

from pandas import DataFrame
from solidago import *


def test_users():
    users = Users(DataFrame([
        ["aidjango", 12521],
        ["le_science4all", 1325],
    ], columns=["username", "n_comparisons"]))
    assert len(users) == 2
    assert users["aidjango"]["n_comparisons"] == 12521
    assert len(users[{"aidjango", "le_science4all"}]) == 2

def test_vector_users():
    users = VectorUsers(np.array([
        [0, 1, 2],
        [3, 4, 5],
    ]), [
        ["aidjango", 12521],
        ["le_science4all", 1325],
    ], columns=["username", "n_comparisons"])
    users = Users([
        User("aidjango", [0, 1, 2], n_comparisons=12521),
        User("le_science4all", [3, 4, 5], n_comparisons=1325),
    ])
    assert len(users) == 2
    assert users["aidjango"]["n_comparisons"] == 12521
    assert len(users[{"aidjango", "le_science4all"}]) == 2
