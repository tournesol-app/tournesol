import numpy as np

from solidago import *
from solidago.primitives.datastructure import SelectLast


def test_comparisons():
    comparisons = Comparisons(default_select=SelectLast())
    keys = ["username", "criterion", "left_name", "right_name", "value", "max"]
    comparisons.set(None, None, **dict(zip(keys, ["user_0", "default", "entity_4", "entity_2", 5, 10])))
    comparisons.set(None, None, **dict(zip(keys, ["user_0", "default", "entity_4", "entity_2", 8, 10])))
    assert len(comparisons) == 2
    assert len(comparisons.filters(username="user_2")) == 0
    kwargs = dict(zip(keys[:4], ["user_0", "default", "entity_4", "entity_2"]))
    assert comparisons.get(None, False, **kwargs)["value"] == 8
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
    