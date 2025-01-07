import pytest
from solidago import *


def test_made_public():
    made_public = MadePublic()
    made_public["aidjango", "entity_4"] = False
    made_public["le_science4all", "entity_4"] = True
    assert not made_public["aidjango", "entity_4"]
    assert made_public["le_science4all", "entity_4"]
