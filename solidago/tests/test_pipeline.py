import pytest
from importlib import import_module
from solidago.pipeline import Pipeline
from solidago.pipeline.inputs import TournesolInputFromPublicDataset

@pytest.mark.parametrize("test", range(5))
def test_pipeline_test_data(test):
    td = import_module(f"data.data_{test}")
    Pipeline()(td.users, td.vouches, td.entities, td.privacy, td.judgments)

