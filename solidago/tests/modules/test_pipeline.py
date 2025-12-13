import pytest
from solidago import *

pipeline = load("tests/modules/test_pipeline.yaml", max_workers=2)
assert isinstance(pipeline, Sequential)


def test_pipeline_generated_data():
    pipeline(Poll.load("tests/saved/0"))

def test_pipeline_tiny_tournesol():
    pipeline(TournesolExport("tests/tiny_tournesol.zip"))
