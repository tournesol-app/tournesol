from backend.cache_timeout_maxmem import cache_timeout_maxmem


def test_cache_timeout_maxmem():
    # for side effects
    arr = []

    def f(x, y, arr=arr):
        arr.append((x, y))
        return x * y

    g = cache_timeout_maxmem(timeout_s=10, max_entries=1)(f)

    # calling first time -> must call f
    assert g(x=1, y=1) == 1
    assert len(arr) == 1
    assert arr[0] == (1, 1)

    # calling second time -> no call to f
    assert g(x=1, y=1) == 1
    assert len(arr) == 1
    assert arr[0] == (1, 1)

    # calling with other args -> call to f
    assert g(x=1, y=2) == 2
    assert len(arr) == 2
    assert arr[1] == (1, 2)

    # calling third time, but cache size only 1
    assert g(x=1, y=1) == 1
    assert len(arr) == 3
    assert arr[2] == (1, 1)
