import pytest
from solidago import *


def test_comparisons():
    comparisons = Comparisons()
    comparisons["user_0", "default", "entity_4", "entity_2"] = [ dict(comparison=5) ]
    comparisons.add_row(["user_0", "default", "entity_4", "entity_2"], dict(comparison=8))
    assert len(comparisons["user_2"]) == 0
    for (username, criterion, left_name, right_name), comparison_list in comparisons:
        for comparison in comparison_list:
            assert isinstance(comparison, Comparison)
    assert comparisons.get_evaluators("entity_2") == {"user_0"}
    ordered_comparisons = comparisons.order_by_entities()
    assert "entity_2" in ordered_comparisons
    assert "entity_4" in ordered_comparisons
    assert "entity_4" in ordered_comparisons["entity_2"]
    
