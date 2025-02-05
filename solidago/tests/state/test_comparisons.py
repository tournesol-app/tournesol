import pytest
from solidago import *


def test_comparisons():
    comparisons = Comparisons()
    comparisons.set("user_0", "default", "entity_4", "entity_2", value=5, max=10)
    comparisons.set("user_0", "default", "entity_4", "entity_2", value=8, max=10)
    assert len(comparisons["user_2"]) == 0
    for (username, criterion, left_name, right_name), comparison in comparisons.iter("rows"):
        assert isinstance(comparison, Comparison)
    assert comparisons.get_evaluators("entity_2") == {"user_0"}
    ordered_comparisons = comparisons.order_by_entities()
    assert "entity_2" in ordered_comparisons
    assert "entity_4" in ordered_comparisons
    assert "entity_4" in ordered_comparisons["entity_2"]
    
    entity_name2index = { "entity_2": 0, "entity_4": 1 }
    indices = comparisons.compared_entity_indices(entity_name2index, False)
    assert indices["left"] == [1, 1]
    assert indices["right"] == [0, 0]
    normalized_comparisons = comparisons.normalized_comparisons(False)
    assert normalized_comparisons[0] == 0.5
    
    indices = comparisons.compared_entity_indices(entity_name2index, True)
    assert indices["left"] == [1]
    assert indices["right"] == [0]
    normalized_comparisons = comparisons.normalized_comparisons(True)
    assert normalized_comparisons[0] == 0.8
