from solidago.pipeline.inputs import TournesolInputFromPublicDataset
from solidago.judgments import Judgments, DataFrameJudgments

def test_tournesol_import():
    inputs = TournesolInputFromPublicDataset("tests/data/tiny_tournesol.zip")
    judgments = Judgments.from_tournesol(inputs, "largely_recommended")
    assert "aidjango" in set(judgments.comparisons["public_username"])
