import numpy as np
from solidago import *


def test_vouches():
    vouches = Vouches()
    vouches.set(by="aidjango", to="le_science4all", kind="Personhood", weight=0.2)
    vouches.set(by="aidjango", to="le_science4all", kind="Personhood", weight=0.5)
    assert vouches.get(by="aidjango", to="le_science4all", kind="Personhood")["weight"] == 0.5
    assert vouches.get(by="le_science4all", to="aidjango", kind="Personhood")["weight"] == 0.0
    assert vouches.get(by="le_science4all", to="aidjango", kind="Personhood")["priority"] == 0.0
