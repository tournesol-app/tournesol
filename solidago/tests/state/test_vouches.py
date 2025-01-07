import pytest
from solidago import *


def test_vouches():
    vouches = Vouches()
    vouches["aidjango", "le_science4all", "Personhood"] = 0.5, 0
    assert vouches["aidjango", "le_science4all", "Personhood"] == (0.5, 0)
    assert vouches["le_science4all", "aidjango", "Personhood"] == (0, - float("inf"))
