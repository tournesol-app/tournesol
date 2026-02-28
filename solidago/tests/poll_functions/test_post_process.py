import pytest
import numpy as np

from solidago import *
from solidago.poll.scoring import *
from solidago.poll_functions.post_process import Squash


user_models = UserModels(
    user_directs=UserDirectScores([
        ("user_0", "entity_0", "default", 2, 1, .5),
        ("user_0", "entity_1", "default", 1, .2, .1),
        ("user_0", "entity_3", "default", .2, .4, .3),
        ("user_1", "entity_0", "default", -1.2, 1, .5),
        ("user_1", "entity_2", "default", -.3, .2, .1),
        ("user_1", "entity_3", "default", .4, .4, .3),
    ], columns=["username", "entity_name", "criterion", "value", "left_unc", "right_unc"])
)
global_model = ScoringModel(
    directs=DirectScores([
        ("entity_0", "default", -1.2, 1, .5),
        ("entity_1", "default", -.2, .5, .5),
        ("entity_2", "default", -.3, .2, .1),
        ("entity_3", "default", .4, .4, .3),
    ], columns=["entity_name", "criterion", "value", "left_unc", "right_unc"])
)

def test_squash():
    post_user_models, _ = Squash(score_max=100)(user_models, global_model)
    score = post_user_models["user_0"](Entity("entity_1"), "default")
    assert score.value == pytest.approx(100/np.sqrt(2), 1e-3)

