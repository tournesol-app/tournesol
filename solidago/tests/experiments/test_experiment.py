import pytest
from solidago import *

def test_experiment():
    source = "tests/experiments/engagement_bias.yaml"
    experiment = Experiment.load(source, ignore_ongoing_run=True)
    experiment()