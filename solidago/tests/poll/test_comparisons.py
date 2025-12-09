import pytest
from solidago import *


def test_comparisons():
    comparisons = Comparisons()
    comparisons["user_0", "default", "entity_4", "entity_2"] = Comparison(value=5, max=10)
    comparisons["user_0", "default", "entity_4", "entity_2"] = Comparison(8, 10)
    assert len(comparisons["user_2"]) == 0
    assert comparisons["user_0", "default", "entity_4", "entity_2"].value == 8
    assert comparisons["user_0", "default", "entity_2", "entity_4"].value == - 8
    for (username, criterion, left_name, right_name), comparison in comparisons:
        assert isinstance(comparison, Comparison)
    assert comparisons.get_evaluators("entity_2") == {"user_0"}
    assert "entity_2" in comparisons.keys("entity_name")
    assert "entity_4" in comparisons.keys("entity_name")
    assert "entity_4" in comparisons.get(entity_name="entity_2").keys("other_name")
    
    entities = Entities(["entity_4", "entity_2"])
    left_right_indices = comparisons.left_right_indices(entities)
    normalized_comparison_list = comparisons.normalized_comparison_list()
    assert left_right_indices == ([0], [1])
    assert normalized_comparison_list == [0.8]
    
    compared_entity_indices = comparisons.compared_entity_indices(entities)
    entity_normalized_comparisons = comparisons.entity_normalized_comparisons(entities)
    
    assert compared_entity_indices[0] == [1]
    assert compared_entity_indices[1] == [0]
    assert entity_normalized_comparisons[0] == [0.8]
    assert entity_normalized_comparisons[1] == [- 0.8]
