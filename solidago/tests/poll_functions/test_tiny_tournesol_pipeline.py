from solidago import *


def test_pipeline_tiny_tournesol():
    pipeline = load("src/solidago/poll_functions/tournesol_full.yaml", max_workers=1)
    assert isinstance(pipeline, Sequential)
    tournesol_export = TournesolExport("tests/tiny_tournesol.zip")
    p0 = pipeline[0].poll2poll_function(tournesol_export)
    p1 = pipeline[1].poll2poll_function(p0)
    p2 = pipeline[2].poll2poll_function(p1)
    p3 = pipeline[3].poll2poll_function(p2)
    p4 = pipeline[4].poll2poll_function(p3)
    p5 = pipeline[5].poll2poll_function(p4)
    p6 = pipeline[6].poll2poll_function(p5)
    p7 = pipeline[7].poll2poll_function(p6)
 