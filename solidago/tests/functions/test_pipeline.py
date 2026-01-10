from solidago import *

pipeline = load("tests/functions/test_pipeline.yaml", max_workers=1)
assert isinstance(pipeline, Sequential)


def test_pipeline_generated_data():
    pipeline(Poll.load("tests/saved/0"))

def test_pipeline_tiny_tournesol():
    pipeline(TournesolExport("tests/tiny_tournesol.zip"))
 