from solidago import *


def test_pipeline_generated_data():
    pipeline = load("tests/functions/test_pipeline.yaml", max_workers=1)
    assert isinstance(pipeline, Sequential)
    pipeline(Poll.load("tests/saved/0"))

def test_pipeline_tiny_tournesol():
    pipeline = load("src/solidago/functions/tournesol_full.yaml", max_workers=1)
    assert isinstance(pipeline, Sequential)
    pipeline(TournesolExport("tests/tiny_tournesol.zip"))
 