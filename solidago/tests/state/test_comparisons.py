import pytest
from solidago import *


def test_comparisons():
    comparisons = Comparisons()
    comparisons["user_0", "default", "entity_4", "entity_2"] = [ dict(comparison=5, comparison_max=10) ]
    comparisons.add_row(["user_0", "default", "entity_4", "entity_2"], dict(comparison=8, comparison_max=10))
    assert len(comparisons["user_2"]) == 0
    for (username, criterion, left_name, right_name), comparison in comparisons.iter("rows"):
        assert isinstance(comparison, Comparison)
    assert comparisons.get_evaluators("entity_2") == {"user_0"}
    ordered_comparisons = comparisons.order_by_entities()
    assert "entity_2" in ordered_comparisons
    assert "entity_4" in ordered_comparisons
    assert "entity_4" in ordered_comparisons["entity_2"]
    
    entity_name2index = { "entity_2": 0, "entity_4": 1 }
    indices = comparisons.compared_entity_indices(entity_name2index)
    assert indices["left"] == [1, 1]
    assert indices["right"] == [0, 0]
    normalized_comparisons = comparisons.normalized_comparisons()
    assert normalized_comparisons[0] == 0.5
