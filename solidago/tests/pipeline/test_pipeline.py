import pytest
from solidago import *

pipeline= Sequential.load("tests/pipeline/test_pipeline.json")


def test_pipeline_generated_data():
    pipeline(State.load("tests/pipeline/saved/0"))

def test_pipeline_tiny_tournesol():
    pipeline(TournesolExport("tests/tiny_tournesol.zip"))

