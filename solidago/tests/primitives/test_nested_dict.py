import pytest

from solidago.primitives.datastructure.nested_dict import NestedDict

def test_nested_dict():
    d = NestedDict(lambda: 0, 3)
    d[0, 1, 2] = 3
    d[0, 2, 2] = 4
    assert d[0, 1, 2] == 3 and d[0][2, 2] == 4
    assert d[0, 3, 2] == 0
    assert d[0, 1].depth == 1
    assert (0, 1, 2) in d
    assert (0, 1, 3) not in d
    assert len(d) == 2
    del d[0, 2, 2]
    assert (0, 2, 2) not in d
    d2 = NestedDict(lambda: 0, 3)
    d2[1, 1, 1] = 1
    d2[1, 2, 2] = 2
    assert len(d | d2) == 3

