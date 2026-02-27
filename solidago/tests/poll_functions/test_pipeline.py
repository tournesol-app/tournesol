from solidago import *


def test_pipeline_tiny_tournesol():
    pipeline = load("src/solidago/poll_functions/tournesol_full.yaml", max_workers=1)
    assert isinstance(pipeline, Sequential)
    pipeline(TournesolExport("tests/tiny_tournesol.zip"))
 