import pytest
from solidago.primitives import pairs

@pytest.mark.parametrize("elements", [10, {"hello", "goodbye", "whatever"}])
def test_pairs(elements):
    p = pairs.UnorderedPairs(elements)
    assert set([ p.index_to_pair(i) for i in range(p.n_pairs) ]) == set(p)

def test_n_samples_range():
    assert len(set(pairs.UnorderedPairs(10).n_samples(10))) == 10

def test_n_samples_iterable():
    assert len(set(pairs.UnorderedPairs({"hello", "goodbye", "whatever"}).n_samples(10))) == 3
        
