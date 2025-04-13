import pytest
from pandas import DataFrame

from solidago.primitives.datastructure.objects import Object, Objects


def test_objects():
    objects = Objects([1, 2, 3])
    assert objects[1].name == 1
    assert 2 in objects
    assert 0 not in objects
    objects.add(Object(5))
    assert 5 in objects
    objects2 = objects.assign(n_actions=0)
    assert objects2[1].n_actions == 0
    embedded_objects = Objects(DataFrame([
        ["object1", 5, 1.2, 0, -1],
        ["object2", 1, 1/3, 0.31, -2],
        ["object3", 2, 2/3, -.12, 10],
    ], columns=["name", "n_actions", "vector_0", "vector_1", "vector_2"]))
    assert len(embedded_objects) == 3
    assert len(embedded_objects["object1"].vector) == 3
    embedded_objects2 = embedded_objects.assign(
        trust=[1.2, 2.2, 3], 
        n_houses={"object1": 2, "object2": 5, "object3": 0}
    )
    assert embedded_objects2["object3"].trust == 3
    assert embedded_objects2["object2"].n_houses == 5
    assert "object3" in embedded_objects
    assert embedded_objects
    
