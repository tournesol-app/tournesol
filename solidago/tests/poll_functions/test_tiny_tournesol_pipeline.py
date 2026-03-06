from solidago import *


def test_pipeline_tiny_tournesol():
    pipeline = poll_functions.TournesolFull(max_workers=1)
    tournesol_export = TournesolExport("tests/tiny_tournesol.zip")
    p0 = pipeline[0](tournesol_export)
    p1 = pipeline[1](p0)
    p2 = pipeline[2](p1)
    p3 = pipeline[3](p2)
    p4 = pipeline[4](p3)
    p5 = pipeline[5](p4)
    p6 = pipeline[6](p5)
    p7 = pipeline[7](p6)
    p8 = pipeline[8](p7)
 