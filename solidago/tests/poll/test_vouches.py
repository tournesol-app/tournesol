from solidago import *
from solidago.primitives.datastructure.filtered_table import SelectLast


def test_vouches():
    vouches = Socials(default_select=SelectLast())
    vouches.set(by="aidjango", to="le_science4all", kind="Personhood", weight=0.2)
    vouches.set(by="aidjango", to="le_science4all", kind="Personhood", weight=0.5)
    assert vouches.get(by="aidjango", to="le_science4all", kind="Personhood")["weight"] == 0.5
    assert vouches.get(by="le_science4all", to="aidjango", kind="Personhood").get("weight", 0) == 0.0
    assert vouches.get(by="le_science4all", to="aidjango", kind="Personhood").get("priority", 0) == 0
