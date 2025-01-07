import pytest
from solidago import *


def test_entities():
    entities = Entities([
        ["entity_0", "Hello World", 39252],
        ["entity_1", "Brilliant", 541325],
        ["entity_2", "Tournesol tutorial", 158],
    ], columns=["entity_name", "title", "n_views"])
    assert len(entities) == 3
    assert entities.get("entity_0")["title"] == "Hello World"
    assert len(entities.get({"entity_0", "entity_2"})) == 2

def test_vector_entities():
    entities = VectorEntities(np.array([
        [0, 1, 2],
        [3, 4, 5],
        [1, 5, 2]
    ]), [
        ["entity_0", "Hello World", 39252],
        ["entity_1", "Brilliant", 541325],
        ["entity_2", "Tournesol tutorial", 158],
    ], columns=["entity_name", "title", "n_views"])
    assert len(entities) == 3
    assert entities.get("entity_0")["title"] == "Hello World"
    assert len(entities.get({"entity_0", "entity_2"})) == 2
