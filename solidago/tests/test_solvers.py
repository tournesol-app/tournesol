import pytest

from solidago.solvers.dichotomy import solve

def test_dichotomy():
    assert solve(lambda t: t, 1, 0, 3) == pytest.approx(1, abs=1e-4)
    assert solve(lambda t: 2 - t**2, 1, 0, 3) == pytest.approx(1, abs=1e-4)
