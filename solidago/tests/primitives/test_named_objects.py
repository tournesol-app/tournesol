from copy import deepcopy
import numpy as np
import pandas as pd

from solidago.primitives.datastructure.named_objects import SeriesNamedObjects


def test_objects():
    columns = ["name", "pretrust", "v0", "v1", "v2"]
    objects = SeriesNamedObjects([
        ["object_1", True, 5, 2, 0],
        ["object_3", False, 3, -1, 0],
        ["object_4", True, 2, 4, 3],
        ["object_6", True, 1, 0, 0],
    ], columns=columns)

    assert len(objects) == 4
    assert objects
    assert not SeriesNamedObjects([], columns=columns)
    assert "object_1" in objects
    assert "object_2" not in objects
    assert pd.Series(name="object_3") in objects
    assert pd.Series(dict(name="object_5")) not in objects
    assert all(objects.vectors[0] == np.array([5, 2, 0], dtype=np.float64))

    assert objects.name2index("object_1") == 0
    assert objects.name2index("object_4") == 2
    assert objects.index2name(1) == "object_3"
    assert set(objects.names()) == {"object_1", "object_3", "object_4", "object_6"}
    assert objects[0].name == "object_1"
    assert objects[3]["pretrust"] # type: ignore

    objects_copy = deepcopy(objects)

    assert len(objects_copy.sample(2)) == 2
    assert set(objects_copy.sample(10).names()) == set(objects.names())

    objects_copy.append(pd.Series(dict(pretrust=True, v0=2, v1=2, v2=0), name="object_9"))
    objects_copy.append_row("object_7", pd.Series(dict(pretrust=True, v0=2, v1=2, v2=0)))

    assert len(objects_copy) == 6
    assert len(objects) == 4
    assert "object_9" in objects_copy

    objects.set_column("v3", [2, 5, 1, 6])

    assert all(objects.vectors[0] == np.array([5, 2, 0, 2], dtype=np.float64))

    objects2 = objects.assign(v4=[1, 1, 2, 3])

    assert all(objects2.vectors[0] == np.array([5, 2, 0, 2, 1], dtype=np.float64))
    assert all(objects.vectors[0] == np.array([5, 2, 0, 2], dtype=np.float64))
    assert len(list(objects)) == 4
    assert len(list(objects.iter_pairs(False))) == 6
    assert len(list(objects.iter_pairs(True))) == 6