from solidago import *

def test_simple():
    source = "tests/experiments/simple.yaml"
    experiment = Experiment.load(source, max_workers=1, ignore_ongoing_run=True)
    experiment()

def test_engagement_bias():
    source = "tests/experiments/engagement_bias.yaml"
    _ = Experiment.load(source, ignore_ongoing_run=True)
