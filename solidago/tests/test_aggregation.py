import pytest
import importlib

from solidago.aggregation import Aggregation, QuantileStandardizedQrMedian

aggregation = QuantileStandardizedQrMedian(dev_quantile=0.9, lipschitz=0.1, error=1e-5)

@pytest.mark.parametrize( "test", list(range(5)) )
def test_aggregation(test):
    td = importlib.import_module(f"data.data_{test}")
    user_models, global_model = td.pipeline.aggregation(
        td.voting_rights,
        td.standardized_models,
        td.users,
        td.entities
    )
