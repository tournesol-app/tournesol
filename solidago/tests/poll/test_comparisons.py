import numpy as np
from solidago import *


def test_comparisons():
    comparisons = Comparisons()
    comparisons.set(username="user_0", criterion="default", left_name="entity_4", right_name="entity_2", value=5, max=10)
    comparisons.set(username="user_0", criterion="default", left_name="entity_4", right_name="entity_2", value=8, max=10)
    assert len(comparisons) == 2
    assert len(comparisons.filters(username="user_2")) == 0
    assert comparisons.get(username="user_0", criterion="default", left_name="entity_4", right_name="entity_2")["value"] == 8
    for comparison in comparisons:
        assert isinstance(comparison, Comparison)
    
    entities = Entities(dict(name=["entity_4", "entity_2"]))
    entity_comparisons = comparisons.entity_comparisons(entities)
    
    other_indices, comparison_values, comparison_maxs = entity_comparisons[0]
    assert other_indices[0] == np.int64(1)
    assert comparison_values[0] == 5
    assert comparison_maxs[0] == 10
    
    other_indices, comparison_values, comparison_maxs = entity_comparisons[1]
    assert other_indices[0] == np.int64(0)
    assert comparison_values[0] == -5
    assert comparison_maxs[0] == 10
    