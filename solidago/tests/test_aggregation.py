import pytest

from solidago.aggregation import Aggregation
from solidago.aggregation.standardized_qrmed import QuantileStandardizedQrMedian

from solidago.generative_model.test_data import users, entities


aggregation = QuantileStandardizedQrMedian(dev_quantile=0.9, lipschitz=0.1, error=1e-5)

@pytest.mark.parametrize( "test", list(range(5)) )
def test_aggregation(test):
    pass
    # user_models, global_model = aggregation(
    #     voting_rights[test],
    #     user_models[test],
    #     users[test],
    #     entities[test]
    # )
