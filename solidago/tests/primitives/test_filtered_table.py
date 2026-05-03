from solidago.primitives.datastructure.filtered_table import SelectFirst, SelectLast


def test_row():
    import pandas as pd
    from solidago.primitives.datastructure.filtered_table import Row
    from copy import deepcopy

    r = Row(pd.Series(), None, x=2)
    assert "x" in r
    assert "y" not in r

    r["y"] = 3
    assert "y" in r
    assert r["y"] == 3
    assert r == deepcopy(r)
    assert r == Row(pd.Series(dict(x=2, y=3))) 
    assert r == Row(pd.Series(dict(y=3)), x=2) 
    assert r.keys("x") == dict(x=2)
    assert r.to_dict() == dict(x=2, y=3)

def test_filter():
    import numpy as np
    from solidago.primitives.datastructure.filtered_table import Filter, NonUniqueError
    import pytest
    
    f = Filter()
    assert f.keys == dict()
    assert not f
    assert set(f.get_indices(100)) == set(range(100))
    assert f.get_index() == 0
    assert f.get_index(SelectFirst()) == 0
    assert f.get_index(SelectLast()) == -1
    assert f.must_be_filtered_in(dict(x=1))
    assert not f.must_be_filtered_out(dict(x=1))

    g = Filter(np.array([0, 4, 2, 1]), criterion="default")
    assert g.keys == dict(criterion="default")
    assert g
    assert len(g.get_indices(100)) == 4
    assert set(g.get_indices(100)) == {0, 4, 2, 1}
    with pytest.raises(NonUniqueError):
        assert g.get_index() == 0
    assert g.get_index(SelectFirst()) == 0
    assert g.get_index(SelectLast()) == 4
    assert g.must_be_filtered_in(dict(criterion="default"))
    assert not g.must_be_filtered_in(dict(criterion="importance"))
    assert g.must_be_filtered_out(dict(criterion="importance"))
    
    h = f & g
    assert h.keys == dict(criterion="default")
    assert h
    assert len(h.get_indices(100)) == 4
    assert set(h.get_indices(100)) == {0, 4, 2, 1}
    with pytest.raises(NonUniqueError):
        assert h.get_index() == 0
    assert h.get_index(SelectFirst()) == 0
    assert h.get_index(SelectLast()) == 4
    assert h.must_be_filtered_in(dict(criterion="default"))
    assert not h.must_be_filtered_in(dict(criterion="importance"))
    assert h.must_be_filtered_out(dict(criterion="importance"))

    i = Filter(np.array([0, 5]), criterion="default", entity_name="entity_0")
    assert i.keys == dict(criterion="default", entity_name="entity_0")
    assert i
    assert len(i.get_indices(100)) == 2
    assert set(i.get_indices(100)) == {0, 5}
    with pytest.raises(NonUniqueError):
        assert i.get_index() == 0
    assert i.get_index(SelectFirst()) == 0
    assert i.get_index(SelectLast()) == 5
    assert i.must_be_filtered_in(dict(criterion="default", entity_name="entity_0", username="user_5"))
    assert not i.must_be_filtered_in(dict(criterion="default", entity_name="entity_5", username="user_5"))
    assert i.must_be_filtered_out(dict(criterion="default", entity_name="entity_5", username="user_5"))
    
    j = g & i
    assert j.keys == dict(criterion="default", entity_name="entity_0")
    assert j
    assert len(j.get_indices(100)) == 1
    assert set(j.get_indices(100)) == {0}
    assert j.get_index() == 0
    assert j.get_index(SelectFirst()) == 0
    assert j.get_index(SelectLast()) == 0
    assert j.must_be_filtered_in(dict(criterion="default", entity_name="entity_0", username="user_5"))
    assert not j.must_be_filtered_in(dict(criterion="default", entity_name="entity_5", username="user_5"))
    assert j.must_be_filtered_out(dict(criterion="default", entity_name="entity_5", username="user_5"))

    k = i.__or__(Filter(np.array([0, 4]), criterion="default", entity_name="entity_0"), 6, 4)
    assert len(k.get_indices(100)) == 4
    assert set(k.get_indices(100)) == {0, 5, 6, 10}

    l = k & g
    assert len(l.get_indices(100)) == 1
    assert set(l.get_indices(100)) == {0}

    l.add_index(np.int64(4))
    l.remove_index(np.int64(0))
    assert l.get_index() == 4

    k.add_index(np.int64(11))
    assert len(k.get_indices(100)) == 5


def test_cache():
    from solidago.primitives.datastructure.filtered_table import _TableCache
    import numpy as np
    
    cache = _TableCache(dict(criterion={"default": [1, 4, 2], "important": [0, 3]}))
    assert cache.keynames() == {"criterion"}
    assert cache.keys("criterion") == {"default", "important"}
    
    cache.add(np.int64(5), "criterion", "default")
    assert set(cache.indices("criterion", "default")) == {1, 2, 4, 5}
    cache.remove(np.int64(1), "criterion", "default")
    assert set(cache.indices("criterion", "default")) == {2, 4, 5}

    cache2 = _TableCache(dict(criterion={"default": [2, 8], "important": [6, 7]}))
    c = cache | cache2
    assert set(c.indices("criterion", "default")) == {2, 4, 5, 8}
    assert set(c.indices("criterion", "important")) == {0, 3, 6, 7}


def test_table():
    from solidago.primitives.datastructure.filtered_table import _Table
    import pandas as pd, numpy as np

    table = _Table(pd.DataFrame([
        ["user_3", "entity_5", 5],
        ["user_5", "entity_3", 3],
        ["user_5", "entity_3", 5],
    ], columns=["username", "entity_name", "value"]))
    assert len(table) == 3
    assert table.keys("username") == {"user_3", "user_5"}
    assert set(table.indices("entity_name", "entity_5")) == {0}
    assert set(table.indices("entity_name", "entity_3")) == {1, 2}
    assert "entity_name" in table._cache.keynames()
    assert set(table.get_filter(username="user_5").get_indices(100)) == {1, 2}
    
    table2 = table.add_columns(x=0)
    assert table2.keys("username") == {"user_3", "user_5"}
    table2.set_column("username", ["user_2", "user_3", "user_4"])
    assert list(table2.df["x"]) == [0, 0, 0]
    assert list(table2.df["username"]) == ["user_2", "user_3", "user_4"]

    table.set_columns(criterion="default", timestamp=[1, 2, 5])
    assert list(table.df["criterion"]) == ["default", "default", "default"]
    assert list(table.df["username"]) == ["user_3", "user_5", "user_5"]

    table.append_row(pd.Series(dict(username="user_6", entity_name="entity_0", criterion="default", value=4, timestamp=3)))
    table.append_row(dict(username="user_2", entity_name="entity_1", criterion="important", value=7, timestamp=7))
    assert len(table) == 5
    assert table.df.loc[4, "criterion"] == "important"
    
    table3 = _Table(pd.DataFrame([
        ["user_1", "entity_2", "default", 31, 5],
        ["user_2", "entity_4", "default", 13, 15],
    ], columns=["username", "entity_name", "criterion", "timestamp", "value"]))
    table4 = table | table3
    assert len(table4) == 7
    assert table4.df.loc[5, "entity_name"] == "entity_2"
    table4.set(np.int64(5), "entity_name", "entity_6")
    assert table4.df.loc[5, "entity_name"] == "entity_6"


def test_filtered_table():
    import pytest
    import pandas as pd
    from solidago.primitives.datastructure.filtered_table import Row, RowFilteredTable, NonUniqueError
    
    columns = ["username", "entity_name", "value"]
    t = RowFilteredTable([
        ["user_3", "entity_5", 5],
        ["user_5", "entity_3", 3],
        ["user_5", "entity_3", 5],
    ], columns=columns)
    assert t
    assert len(t) == 3
    assert t.row_factory(x=2).to_dict() == dict(x=2)
    assert set(t.columns) == set(columns)
    assert t.n_columns == 3
    assert not t.filter
    assert set(t.indices) == set(range(3))

    t.cache("username")
    assert t.table._cache.keynames() == {"username"}
    assert t.table._cache.keys("username") == {"user_3", "user_5"}
    assert set(t.table._cache.indices("username", "user_3")) == {0}
    assert set(t.table._cache.indices("username", "user_5")) == {1, 2}
    t.append_series(pd.Series(dict(username="user_9", entity_name="entity_2", value=2)))
    t.append_series(dict(zip(columns, ("user_9", "entity_0", 2))))
    t.append(("user_3", "entity_0", 1))
    assert len(t) == 6
    assert t.table._cache.keys("username") == {"user_3", "user_5", "user_9"}
    assert set(t.table._cache.indices("username", "user_9")) == {3, 4}
    assert set(t.table._cache.indices("username", "user_3")) == {0, 5}
    
    t.cache("entity_name", "value")
    assert t.table._cache.keynames() == {"username", "entity_name", "value"}
    assert t.table._cache.keys("entity_name") == {"entity_3", "entity_5", "entity_2", "entity_0"}
    assert set(t.table._cache.indices("entity_name", "entity_2")) == {3}
    assert set(t.table._cache.indices("value", 5)) == {0, 2}
    assert set(t.table._cache.indices("username", "user_9")) == {3, 4}

    assert t.df.loc[0, "username"] == "user_3"
    assert t.keys("username") == {"user_3", "user_5", "user_9"}
    assert t.multikeys("username", "entity_name") == {
        ("user_3", "entity_0"), ("user_3", "entity_5"), ("user_5", "entity_3"), ("user_9", "entity_0"), ("user_9", "entity_2")
    }
    assert t.get_keys(Row(username="user_4", entity_name="entity_0"), {"username"}) == dict(username="user_4")
    assert len(list(t.iter_filters("username"))) == 3
    f = dict(t.iter_filters("username"))[("user_5",)]
    assert f.indices is not None
    assert len(f.indices) == 2
    subtable = dict(t.iter("username", "entity_name"))[("user_5", "entity_3")]
    assert isinstance(subtable, RowFilteredTable)
    assert len(subtable) == 2

    s = t.filters(username="user_9")
    assert s.filter.indices is not None
    assert set(s.filter.indices) == {3, 4}
    assert s.filter.keys == dict(username="user_9")
    assert len(s) == 2
    assert set(s.get_column("value")) == {2}
    
    assert t.get_index(username="user_9", entity_name="entity_2") == 3
    assert t.get(username="user_9", entity_name="entity_2")["value"] == 2
    assert not t.filters(username="user_9", entity_name="entity_1")
    with pytest.raises(NonUniqueError):
        t.get(username="user_5", entity_name="entity_3")
    assert t.get(username="user_5", entity_name="entity_3", select=SelectFirst())["value"] == 3
    assert t.filters(username="user_9").get(entity_name="entity_2")["value"] == 2
    assert len(t.filters(username="user_9")) == 2
    assert "user_9" in t.filters(entity_name="entity_0").keys("username")
    
    s = RowFilteredTable([["user_2", "entity_2", 0]], columns=columns)
    assert len(t | s) == 7
    assert len(t) == 6
    assert len(s) == 1

    g = t.filters(username="user_9")
    g.append(("user_7", "entity_5", 4))
    assert len(g) == 2
    assert len(t) == 7
    assert not t.filters(username="user_9", entity_name="entity_3")
    assert t.get(username="user_9", entity_name="entity_2")["value"] == 2
    assert t.get(username="user_7", entity_name="entity_5")["value"] == 4
    assert t.keys("entity_name") == {"entity_0", "entity_2", "entity_3", "entity_5"}
