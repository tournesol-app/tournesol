import pytest
from solidago import *


def test_vouches():
    vouches = Vouches()
    vouches.set("aidjango", "le_science4all", "Personhood", 0.5, 0)
    assert vouches.get("aidjango", "le_science4all", "Personhood") == (0.5, 0)
    assert vouches.get("le_science4all", "aidjango", "Personhood") == (0, - float("inf"))
