import pytest
from solidago import *

def test_user_models():
    entities = Entities(["entity_1", "entity_2", "entity_3"])
    direct = UserModels(
        user_directs=MultiScore(
            data=[
                ("aidjango", "entity_1", "default", 2, 1, 1),
                ("aidjango", "entity_1", "importance", 0, 1, 1),
                ("aidjango", "entity_2", "default", -1, 1, 1),
                ("aidjango", "entity_2", "importance", 3, 1, 10),
                ("aidjango", "entity_3", "default", 0, 0, 1),
                ("le_science4all", "entity_1", "default", 0, 0, 0),
                ("le_science4all", "entity_1", "importance", -3, 1, 1),
                ("le_science4all", "entity_2", "default", -1, 0, 1),
            ],
            key_names=["username", "entity_name", "criterion"]
        )
    )
    scaled = direct.scale(
        MultiScore(
            data=[
                ("aidjango", "default", "multiplier", 2, 0.1, 1),
                ("aidjango", "default", "translation", -1, 1, 1),
                ("le_science4all", "default", "multiplier", 1, 0, 0),
                ("le_science4all", "default", "translation", 1, 1, 1),
            ],
            key_names=["username", "criterion", "kind"]
        ),
        note="second"
    )
    rescaled = scaled.scale(
        MultiScore(
            data=[
                ("default", "multiplier", 2, 0, 0),
                ("default", "translation", 1, 0, 0),
                ("importance", "multiplier", 1, 0, 1),
                ("importance", "translation", 3, 2, 2),
            ],
            key_names=["criterion", "kind"]
        ),
        note="second"
    )
    post_processed = rescaled.post_process("SquashedModel", max_score=100., note="squash")
    
    assert post_processed(entities).get("le_science4all", "entity_1", "importance").value == 0
    assert post_processed["aidjango"]("entity_3").get("importance").isnan()
    assert post_processed["aidjango"]("entity_2").get("importance") > 0
