import pytest
from solidago import *

def test_user_models():
    entities = Entities(["entity_1", "entity_2", "entity_3"])
    user_models = UserModels({
        "aidjango": DirectScoring({
            "entity_1": {
                "default": (2, 1, 1),
                "importance": (0, 1, 1),
            },
            "entity_2": {
                "default": (-1, 1, 1),
                "importance": (3, 1, 10),
            },
            "entity_3": {
                "default": (0, 0, 1),
            },
        }),
        "le_science4all": DirectScoring({
            "entity_1": {
                "default": (0, 0, 0),
                "importance": (-3, 1, 1),
            },
            "entity_2": {
                "default": (-1, 0, 1),
            },
        })
    })
    scaled_models = UserModels({
        username: ScaledModel(model, ScaleDict({
            "default": (2, 0, 0, 1, 0, 0),
            "importance": (1, 0, 1, 3, 2, 2),
        })) for username, model in user_models
    })
    processed_models = UserModels({
        username: SquashedModel(model, 100) 
        for username, model in scaled_models
    })
    assert processed_models(entities)["le_science4all", "entity_1", "importance"].value == 0
    assert processed_models["aidjango"]("entity_3")["importance"].isnan()
    assert processed_models["aidjango"]("entity_2")["importance"] > 0
