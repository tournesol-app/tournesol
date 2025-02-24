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
    s = MultiScore([("default", 1, 4, 2), ("importance", 2, 1, 0)])
    s.add_row("fun", 1, 0, 2)
    assert s.get("fun") + s.get("importance") == Score(3, 1, 2)
    assert s.get("diversity").isnan()
    t = MultiScore([("default", 1, 0, 0)])
    assert (s*t).get("default") == s.get("default")
    assert (s*t).get("importance").isnan()
    assert (s+t).get("default").average_uncertainty() == 3

def test_direct():
    direct = DirectScoring()
    entities = Entities(["entity_1", "entity_2"])
    direct.set("entity_1", "default", Score(1, 5, 2))
    direct.set("entity_2", "default", 2, 3, 1)
    direct.set("entity_2", "importance", 2, 0, 1)
    scaled = ScaledModel(
        parent=direct, 
        scales=MultiScore([
            ["default", "multiplier", 1, 0, 0],
            ["default", "translation", 1, 0, 0],
            ["importance", "multiplier", 2, 1, 1],
            ["importance", "translation", 3, 2, 0],
        ], key_names=["criterion", "kind"])
    )
    post_process = SquashedModel(scaled, 100)
    assert post_process("entity_1").get("importance").isnan()
    assert post_process("entity_2").get("importance") > 0
    assert len(post_process(entities)) == 3
    assert scaled(entities).get("entity_1", "default") == Score(2, 5, 2)
