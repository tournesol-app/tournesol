import pytest
from solidago import *

pipeline= Sequential.load("tests/pipeline/test_pipeline.json")


def test_pipeline_test_data():
    pipeline(State.load("tests/pipeline/saved/0"))

