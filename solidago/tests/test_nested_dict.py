import pytest

from solidago.state.wrappers.nested_dict


def test_nested_dict():
    d = NestedDict(
        keys_names=["animal", "food"], 
        values_names: ["a", "b"],
        d={ "elephant": { "water": (1, 0) }, "dog": { "meat": (2, 3) } },
        None
    )
