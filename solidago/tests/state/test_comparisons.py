import pytest
from solidago import *


def test_comparisons():
    comparisons = Comparisons()
    comparisons.set("user_0", "default", "entity_4", "entity_2", value=5, max=10)
    comparisons.set("user_0", "default", "entity_4", "entity_2", value=8, max=10)
    assert len(comparisons.get("user_2")) == 0
    for (username, criterion, left_name, right_name), comparison in comparisons:
        assert isinstance(comparison, Comparison)
    assert comparisons.get_evaluators("entity_2") == {"user_0"}
    ordered_comparisons = comparisons.order_by_entities(other_keys_first=False)
    assert "entity_2" in set(ordered_comparisons["entity_name"])
    assert "entity_4" in set(ordered_comparisons["entity_name"])
    assert "entity_4" in set(ordered_comparisons.get("entity_2")["other_name"])
    
    entity_name2index = { "entity_2": 0, "entity_4": 1 }
    indices = comparisons.compared_entity_indices(entity_name2index, True)
    assert indices["left"] == [1]
    assert indices["right"] == [0]
    normalized_comparisons = comparisons.normalized_comparisons()
    assert normalized_comparisons[0] == 0.8
