import pytest
from solidago import *


def test_made_public():
    made_public = MadePublic()
    made_public.set(False, "aidjango", "entity_4")
    made_public.set(True, "le_science4all", "entity_4")
    assert not made_public.get("aidjango", "entity_4")
    assert made_public.get("le_science4all", "entity_4")
