import pytest
from solidago import *

pipeline = Sequential.load("tests/modules/test_pipeline.json", max_workers=2)


def test_pipeline_generated_data():
    pipeline(State.load("tests/saved/0"))

def test_pipeline_tiny_tournesol():
    pipeline(TournesolExport("tests/tiny_tournesol.zip"))
