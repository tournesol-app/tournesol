import pytest
from solidago import *

def test_user_models():
    entities = Entities(["entity_1", "entity_2", "entity_3"])
    user_models = UserModels(MultiScore(["username", "entity_name", "criterion"], {
        ("aidjango", "entity_1", "default"): Score(2, 1, 1),
        ("aidjango", "entity_1", "importance"): Score(0, 1, 1),
        ("aidjango", "entity_2", "default"): Score(-1, 1, 1),
        ("aidjango", "entity_2", "importance"): Score(3, 1, 10),
        ("aidjango", "entity_3", "default"): Score(0, 0, 1),
        ("le_science4all", "entity_1", "default"): Score(0, 0, 0),
        ("le_science4all", "entity_1", "importance"): Score(-3, 1, 1),
        ("le_science4all", "entity_2", "default"): Score(-1, 0, 1),
    }))
    scaled = user_models.scale(MultiScore(["username", "kind", "criterion"], {
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
    processed = rescaled.post_process("SquashedModel", score_max=100., note="squash")
    
    assert processed(entities)["le_science4all", "entity_1", "importance"].value == 0
    assert processed["aidjango"]("entity_3")["importance"].isnan()
    assert processed["aidjango"]("entity_2")["importance"] > 0
