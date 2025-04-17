import pytest
from solidago import *

def test_user_models():
    entities = Entities(["entity_1", "entity_2", "entity_3"])
    directs = UserModels(MultiScore(["username", "entity_name", "criterion"], {
        ("aidjango", "entity_1", "default"): Score(2, 1, 1),
        ("aidjango", "entity_1", "importance"): Score(0, 1, 1),
        ("aidjango", "entity_2", "default"): Score(-1, 1, 1),
        ("aidjango", "entity_2", "importance"): Score(3, 1, 10),
        ("aidjango", "entity_3", "default"): Score(0, 0, 1),
        ("le_science4all", "entity_1", "default"): Score(0, 0, 0),
        ("le_science4all", "entity_1", "importance"): Score(-3, 1, 1),
        ("le_science4all", "entity_2", "default"): Score(-1, 0, 1),
    }))
    scaled = directs.scale(MultiScore(["username", "kind", "criterion"], {
        ("aidjango", "multiplier", "default"): Score(2, 0.1, 1),
        ("aidjango", "translation", "default"): Score(-1, 1, 1),
        ("aidjango", "multiplier", "importance"): Score(1, 0, 0),
        ("aidjango", "translation", "importance"): Score(0, 0, 0),
        ("le_science4all", "multiplier", "default"): Score(1, 0, 0),
        ("le_science4all", "translation", "default"): Score(1, 1, 1),
    }), note="second")
    rescaled = scaled.scale(MultiScore(["kind", "criterion"], {
        ("multiplier", "default"): Score(2, 0, 0),
        ("translation", "default"): Score(1, 0, 0),
        ("multiplier", "importance"): Score(1, 0, 1),
        ("translation", "importance"): Score(3, 2, 2),
    }), note="third")
    squashed = rescaled.squash(100.)
    
    assert squashed(entities)["le_science4all", "entity_1", "importance"].value == 0
    assert squashed(entities, "default")["le_science4all", "entity_2"].value > 70
    assert squashed["aidjango"]("entity_3")["importance"].isnan()
    assert squashed["aidjango"]("entity_2")["importance"] > 0
