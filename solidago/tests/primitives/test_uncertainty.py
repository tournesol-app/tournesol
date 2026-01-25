from solidago.primitives.uncertainty import *

def test_nll_increase():
    uncertainty = UncertaintyByLossIncrease(nll_increase=1.0, error=1e-1, max=1e3)
    