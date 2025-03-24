import pytest
from solidago import *


def test_comparisons():
    comparisons = Comparisons()
    comparisons["user_0", "default", "entity_4", "entity_2"] = Comparison(value=5, max=10)
    comparisons["user_0", "default", "entity_4", "entity_2"] = Comparison(8, 10)
    assert len(comparisons.get("user_2")) == 0
    for (username, criterion, left_name, right_name), comparison in comparisons:
        assert isinstance(comparison, Comparison)
    assert comparisons.get_evaluators("entity_2") == {"user_0"}
    assert "entity_2" in comparisons.nested_dict("entity_name").key_set()
    assert "entity_4" in comparisons.nested_dict("entity_name").key_set()
    assert "entity_4" in comparisons.nested_dict("entity_name", "other_name")["entity_2"].key_set()
    
    entities = Entities(["entity_4", "entity_2"])
    indices = comparisons.compared_entity_indices(entities)
    assert indices[0] == [1]
    assert indices[1] == [0]
    normalized_comparisons = comparisons.normalized_comparisons(entities)
    assert normalized_comparisons[0] == [0.8]
