import pytest
import numpy as np

from pandas import DataFrame
from solidago import *


def test_entities():
    entities = Entities(DataFrame([
        ["entity_0", "Hello World", 39252],
        ["entity_1", "Brilliant", 541325],
        ["entity_2", "Tournesol tutorial", 158],
    ], columns=["entity_name", "title", "n_views"]))
    assert len(entities) == 3
    assert entities["entity_0"].title == "Hello World"
    assert len(entities[{"entity_0", "entity_2"}]) == 2

def test_entities2():
    entities = Entities(["entity_1", "entity_2"])
    assert set(entities.keys()) == {"entity_1", "entity_2"}

def test_vector_entities():
    entities = Entities([
        Entity("entity_0", [0, 1, 2], title="Hello World", n_views=39252),
        Entity("entity_1", [3, 4, 5], title="Brilliant", n_views=541325),
        Entity("entity_2", [1, 5, 2], title="Tournesol tutorial", n_views=158),
    ])
    assert len(entities) == 3
    assert entities["entity_0"].title == "Hello World"
    assert len(entities[{"entity_0", "entity_2"}]) == 2
