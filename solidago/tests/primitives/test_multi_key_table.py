import pytest
from pandas import DataFrame

from solidago.primitives.datastructure.multi_key_table import MultiKeyTable

def test_multi_key_table():
    t = MultiKeyTable(["username", "entity_name"])
    assert t.depth == 2
    assert not t
    t["user_9", "entity_2"] = 2
    t["user_9", "entity_0"] = 1
    assert t["user_9", "entity_1"] is None
    assert t["user_9", "entity_2"] == 2
    assert t["user_9"]["entity_2"] == 2
    assert len(t[{"user_9"}]) == 2
    assert len(t["user_9", {"entity_0", "entity_2"}]) == 2
    assert len(t["user_9", {"entity_1", "entity_2"}]) == 1
    assert "user_9" in t.get(entity_name="entity_0")
    assert len(t) == len(t.to_df())
    assert t
    s = MultiKeyTable(
        ["username", "entity_name"], 
        DataFrame({ "username": ["user_2"], "entity_name": ["entity_2"], "value": 0 })
    )
    assert len(t | s) == 3
    assert len(t) == 2
    assert len(s) == 1
    g = t["user_9"]
    g["entity_3"] = 5
    assert t["user_9", "entity_3"] == 5
    del g["entity_2"]
    assert t["user_9", "entity_2"] is None
    d = t.nested_dict("entity_name")
    assert "user_9" in d["entity_0"]
