import pytest
from solidago.primitives import pairs

@pytest.mark.parametrize("elements", [10, "abcdefgh", {"hello", "goodbye", "whatever"}])
def test_pairs(elements):
    p = pairs.UnorderedPairs(elements)
    assert set([ p.index_to_pair(i) for i in range(p.n_pairs) ]) == set(p)

@pytest.mark.parametrize("elements", [10, "abcdefgh", {"hello", "goodbye", "whatever"}])
def test_n_samples(elements):
    len(set(pairs.UnorderedPairs(elements).n_samples(10))) == 10
        
