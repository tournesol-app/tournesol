from solidago.pipeline.inputs import TournesolInputFromPublicDataset
from solidago.judgments import Judgments, DataFrameJudgments

def test_tournesol_import():
    inputs = TournesolInputFromPublicDataset("tests/data/tiny_tournesol.zip")
    judgments = inputs.get_judgments("largely_recommended")
    assert "aidjango" in set(judgments.comparisons["public_username"])
