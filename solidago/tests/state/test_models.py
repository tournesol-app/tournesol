import pytest
from solidago import *

def test_score():
    assert Score(1, 0, 0) + Score(1, 0, 0) == Score(2, 0, 0)
    assert Score(1, 1, 0) + Score(1, 0, 1) == Score(2, 1, 1)
    assert (Score(1, 1, 0) * Score(1, 0, 1)).max == 2
    assert Score(1, 1, 1) < Score(3, 0, 2)
    assert Score(1, 1, 2) >= Score(3, 0, 2)
    assert not (Score(1, 1, 2) <= Score(-3, 0, 2))
    assert 4 not in Score(-3, 0, 2).abs()

def test_multiscore():
    s = MultiScore(init_data={"default": Score(1, 4, 2), "importance": Score(2, 1, 0)})
    s["fun"] = Score(1, 0, 2)
    assert s["fun"] + s["importance"] == Score(3, 1, 2)
    assert s["diversity"].isnan()
    t = MultiScore(init_data={"default": Score(1, 0, 0)})
    assert (s*t)["default"] == s["default"]
    assert (s*t)["importance"].isnan()
    assert (s+t)["default"].average_uncertainty() == 3

def test_direct():
    direct = DirectScoring()
    entities = Entities(["entity_1", "entity_2"])
    direct["entity_1", "default"] = Score(1, 5, 2)
    direct["entity_2", "default"] = Score(2, 3, 1)
    direct["entity_2", "importance"] = Score(2, 0, 1)
    scaled = ScaledModel(direct)
    scaled["multiplier", "default"] = Score(1, 0, 0)
    scaled["translation", "default"] = Score(1, 0, 0)
    scaled["multiplier", "importance"] = Score(2, 1, 1)
    scaled["translation", "importance"] = Score(3, 2, 0)
    post_process = SquashedModel(scaled, 100)
    assert post_process("entity_1")["importance"].isnan()
    assert post_process("entity_2")["importance"] > 0
    assert len(post_process(entities)) == 3
    assert scaled(entities)["entity_1", "default"] == Score(2, 5, 2)
